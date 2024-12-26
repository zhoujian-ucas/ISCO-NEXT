from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import torch
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class ModelWrapper(ABC):
    """模型包装器基类"""
    
    @abstractmethod
    def load(self, checkpoint_path: Path):
        """加载模型"""
        pass
    
    @abstractmethod
    def predict(self, data: Any) -> Any:
        """模型预测"""
        pass

class YOLOWrapper(ModelWrapper):
    """YOLO模型包装器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model = None
        
    def load(self, checkpoint_path: Path):
        """加载YOLO模型"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(checkpoint_path))
            logger.info(f"Loaded YOLO model from {checkpoint_path}")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {str(e)}")
            raise

    def predict(self, data: Any) -> Any:
        """YOLO预测"""
        if self.model is None:
            raise RuntimeError("Model not loaded")
        return self.model.predict(data, **self.config.get('inference_params', {}))

class ModelManager:
    """模型管理器"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.checkpoints_dir = self.base_dir / "checkpoints"
        self.configs_dir = self.base_dir / "configs"
        self.models: Dict[str, ModelWrapper] = {}
        
        # 创建必要的目录
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
    
    def register_model(self, plugin_name: str, model_type: str, 
                      config_path: Optional[Path] = None) -> ModelWrapper:
        """注册新模型"""
        # 确定模型检查点目录
        checkpoint_dir = self.checkpoints_dir / plugin_name
        checkpoint_dir.mkdir(exist_ok=True)
        
        # 加载模型配置
        config = {}
        if config_path:
            with open(config_path) as f:
                config = yaml.safe_load(f)
        
        # 创建模型包装器
        if model_type.lower() == 'yolo':
            model = YOLOWrapper(config)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        # 查找最新的检查点
        checkpoints = list(checkpoint_dir.glob("*.pt"))
        if not checkpoints:
            raise FileNotFoundError(f"No checkpoints found in {checkpoint_dir}")
        
        latest_checkpoint = max(checkpoints, key=lambda p: p.stat().st_mtime)
        model.load(latest_checkpoint)
        
        self.models[plugin_name] = model
        return model
    
    def get_model(self, plugin_name: str) -> ModelWrapper:
        """获取模型实例"""
        return self.models.get(plugin_name) 