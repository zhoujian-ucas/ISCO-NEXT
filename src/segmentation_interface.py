from abc import ABC, abstractmethod
import numpy as np

class SegmentationModel(ABC):
    """分割模型接口"""
    
    @abstractmethod
    def segment(self, image: np.ndarray) -> np.ndarray:
        pass

class SAMAdapter(SegmentationModel):
    """SAM模型适配器"""
    def __init__(self, model_path: str):
        # 初始化SAM模型
        pass
        
    def segment(self, image: np.ndarray) -> np.ndarray:
        # 实现SAM分割
        pass

class DINOAdapter(SegmentationModel):
    """DINO模型适配器"""
    def __init__(self, model_path: str):
        # 初始化DINO模型
        pass
        
    def segment(self, image: np.ndarray) -> np.ndarray:
        # 实现DINO分割
        pass 