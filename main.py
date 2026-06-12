import asyncio
import json #用于处理 JSON 数据
import uuid  # 用于生成唯一的任务取件码 (Task ID)
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

# 把写的虚拟设备导入进来
from core_devices import VirtualRobotArm, VirtualMicroscope

# 引入异步版的 FakeRedis，完美平替真实的 Redis
from fakeredis.aioredis import FakeRedis

from pydantic import BaseModel
from zhipuai import ZhipuAI #智谱AI的工具包
   
# 实例化 FastAPI 应用
app = FastAPI(title="企业级容灾 Agent 架构", version="2.0")

# 配置 CORS 跨域允许 ======
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有前端访问
    allow_credentials=True,
    allow_methods=["*"],  # 允许 POST, GET 等所有方法
    allow_headers=["*"],
)

# 实例化大模型与虚拟设备
client = ZhipuAI(api_key="79e049bb823c4074bcbe240ce31a050a.t3uXPkacJIGNnnBG")
arm_01 = VirtualRobotArm("UR5_工业机械臂")
microscope_01 = VirtualMicroscope("Zeiss_Optic_01")

# 初始化 Redis 客户端 (decode_responses=True 表示直接处理字符串而非字节)
redis_client = FakeRedis(decode_responses=True, encoding="utf-8")

class AgentRequest(BaseModel):
    instruction: str

# ==========================================
# 核心组件：后台执行器 (不在主线程堵塞)
# ==========================================
async def background_agent_pipeline(task_id: str, instruction: str):
    try:
        # 1. 更新 Redis 状态：大脑正在思考
        await redis_client.hset(task_id, mapping={"status": "thinking", "progress": "正在呼叫大模型解析指令..."})
        
        system_prompt = """
        你是一个光电自动化实验室的Agent大脑。请将用户的自然语言指令，翻译为JSON任务数组。
        可用设备：
        1. 'UR5_工业机械臂' (action: 'move', params: 'position')
        2. 'Zeiss_Optic_01' (action: 'scan', params: 'target_material')
        只返回JSON，不要包含 ```json 标记。
        格式示例：[{"device": "设备名", "action": "动作名", "params": {"参数名": "参数值"}}]
        """
        
        # 模拟真实网络请求
        response = client.chat.completions.create(
            model="glm-4.5-air",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": instruction}
            ]
        )
        llm_reply = response.choices[0].message.content.replace("```json", "").replace("```", "").strip()
        task_queue = json.loads(llm_reply)

        # 2. 更新 Redis 状态：思考完毕，准备执行
        await redis_client.hset(task_id, mapping={
            "status": "executing", 
            "progress": f"大模型已生成 {len(task_queue)} 步任务，开始调度底层设备..."
        })

        execution_trace = []
        for step, task in enumerate(task_queue):
            # 每执行一步，都实时更新 Redis 里的进度
            current_progress = f"正在执行第 {step + 1}/{len(task_queue)} 步: 操作 {task['device']}"
            await redis_client.hset(task_id, "progress", current_progress)
            
            if task["device"] == arm_01.name:
                res = await arm_01.execute(task["params"])
            elif task["device"] == microscope_01.name:
                res = await microscope_01.execute(task["params"])
            
            execution_trace.append(res)
            
        # 3. 更新 Redis 状态：全部执行完毕
        await redis_client.hset(task_id, mapping={
            "status": "completed", 
            "progress": "所有任务已圆满完成",
            "result": json.dumps(execution_trace, ensure_ascii=False) # 将最终报告存入Redis
        })
        
    except Exception as e:
        # 容灾处理：如果中途崩溃，将错误信息写入 Redis
        await redis_client.hset(task_id, mapping={"status": "failed", "progress": f"系统崩溃: {str(e)}"})


# ==========================================
# 接口1：老板下发任务（秒回取件码）
# ==========================================
@app.post("/api/v1/agent/submit")
async def submit_task(req: AgentRequest, bg_tasks: BackgroundTasks):
    # 生成一个独一无二的随机流水号作为 task_id
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # 在 Redis 中初始化这个任务的状态
    await redis_client.hset(task_id, mapping={"status": "pending", "progress": "任务已接收，等待处理"})
    
    # 将极其耗时的管线操作，扔给 FastAPI 的后台去慢慢跑，不要卡住当前的 HTTP 返回
    bg_tasks.add_task(background_agent_pipeline, task_id, req.instruction)
    
    return {"message": "任务已提交至后台处理！", "task_id": task_id}

# ==========================================
# 接口2：老板凭取件码查询进度
# ==========================================
@app.get("/api/v1/task/{task_id}")
async def check_task_status(task_id: str):
    # 从 Redis 中读取当前任务的最新状态
    task_info = await redis_client.hgetall(task_id)
    if not task_info:
        return {"error": "找不到该任务，取件码错误或已过期"}
    
    # 稍微整理一下输出格式
    if "result" in task_info:
        task_info["result"] = json.loads(task_info["result"])
        
    return task_info
