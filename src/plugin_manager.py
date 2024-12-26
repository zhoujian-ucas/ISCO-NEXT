from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type
import numpy as np
from pathlib import Path
import importlib
import inspect
import logging

logger = logging.getLogger(__name__)

class OrganoidPlugin(ABC):
    """增强的插件基类"""
    
    plugin_type: str = ""  # 插件类型标识
    plugin_name: str = ""  # 插件名称
    version: str = "1.0.0"  # 插件版本
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self._validate_config()
    
    @abstractmethod
    def define_morphology(self) -> Dict[str, Any]:
        """定义形态学特征"""
        pass
    
    @abstractmethod
    def analyze(self, image: np.ndarray) -> Dict[str, Any]:
        """执行形态分析"""
        pass
    
    def _validate_config(self):
        """验证插件配置"""
        required_configs = self.get_required_configs()
        missing = [key for key in required_configs if key not in self.config]
        if missing:
            raise ValueError(f"Missing required configs: {missing}")
    
    @classmethod
    def get_required_configs(cls) -> List[str]:
        """获取必需的配置项"""
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取插件元数据"""
        return {
            "type": self.plugin_type,
            "name": self.plugin_name,
            "version": self.version,
            "config": self.config
        }

def register_plugin(plugin_type: str, plugin_name: str):
    """插件注册装饰器"""
    def decorator(cls):
        cls.plugin_type = plugin_type
        cls.plugin_name = plugin_name
        return cls
    return decorator

class PluginManager:
    """增强的插件管理系统"""
    
    def __init__(self):
        self.plugins: Dict[str, Type[OrganoidPlugin]] = {}
        self.plugin_instances: Dict[str, OrganoidPlugin] = {}
        
    def register_plugin(self, plugin_class: Type[OrganoidPlugin]):
        """注册插件类"""
        key = f"{plugin_class.plugin_type}.{plugin_class.plugin_name}"
        self.plugins[key] = plugin_class
        logger.info(f"Registered plugin: {key}")
        
    def create_plugin(self, plugin_type: str, plugin_name: str, 
                     config: Dict[str, Any] = None) -> OrganoidPlugin:
        """创建插件实例"""
        key = f"{plugin_type}.{plugin_name}"
        if key not in self.plugins:
            raise ValueError(f"Plugin not found: {key}")
            
        plugin_class = self.plugins[key]
        instance = plugin_class(config)
        self.plugin_instances[key] = instance
        return instance
    
    def get_plugin(self, plugin_type: str, plugin_name: str) -> OrganoidPlugin:
        """获取插件实例"""
        key = f"{plugin_type}.{plugin_name}"
        return self.plugin_instances.get(key)
    
    def load_plugins(self, plugin_dir: Path):
        """从目录加载插件"""
        plugin_dir = Path(plugin_dir)
        if not plugin_dir.exists():
            raise ValueError(f"Plugin directory not found: {plugin_dir}")
            
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
                
            try:
                module_name = f"plugins.{plugin_file.stem}"
                spec = importlib.util.spec_from_file_location(
                    module_name, plugin_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # 查找模块中的插件类
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, OrganoidPlugin) and 
                        obj != OrganoidPlugin):
                        self.register_plugin(obj)
                        
            except Exception as e:
                logger.error(f"Error loading plugin {plugin_file}: {str(e)}") 