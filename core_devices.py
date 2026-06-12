import asyncio
from abc import ABC, abstractmethod

# 1. 抽象出所有设备的公共标准
class BaseDevice(ABC):
    def __init__(self, name: str):
        self.name = name
        self.status = "idle"

    @abstractmethod
    async def connect(self):
        pass

    @abstractmethod
    async def execute(self, task_param: dict):
        pass

# 2. 虚拟机械臂
class VirtualRobotArm(BaseDevice):
    async def connect(self):
        print(f"[{self.name}] 初始化通信中... 机械臂已上线。")
        self.status = "connected"

    async def execute(self, task_param: dict):
        self.status = "working"
        target_pos = task_param.get("position", "原点")
        print(f"[{self.name}] 开始移动至坐标: {target_pos}...")
        
        await asyncio.sleep(2) # 模拟运动耗时
        
        print(f"[{self.name}] 移动完成。")
        self.status = "idle"
        return {"status": "success", "position": target_pos}

# 3. 虚拟高分数字显微镜
class VirtualMicroscope(BaseDevice):
    async def connect(self):
        print(f"[{self.name}] 初始化光学传感器... 显微镜已上线。")
        self.status = "connected"

    async def execute(self, task_param: dict):
        self.status = "working"
        target = task_param.get("target_material", "未知样本")
        print(f"[{self.name}] 正在对焦并采集 [{target}] 的光学图像...")
        
        await asyncio.sleep(1.5) # 模拟对焦耗时
        
        print(f"[{self.name}] 图像采集完成。")
        self.status = "idle"
        return {
            "status": "success", 
            "image_url": "https://virtual-lab.local/mock_sample.png",
            "material": target
        }