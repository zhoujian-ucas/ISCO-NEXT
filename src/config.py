from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass
class Config:
    """配置类"""
    model_path: Path
    output_dir: Path
    batch_size: int
    gpu_enabled: bool
    log_level: str
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'Config':
        """从YAML文件加载配置"""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict) 