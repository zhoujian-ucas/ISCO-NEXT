import sys
import subprocess
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

def check_conda_env():
    """检查当前是否在正确的conda环境中"""
    try:
        # 检查是否在conda环境中
        if "conda" not in sys.prefix:
            raise EnvironmentError("Not in a conda environment")
            
        # 检查是否是正确的环境
        result = subprocess.run(
            ["conda", "env", "list"], 
            capture_output=True, 
            text=True
        )
        if "organoid-analysis" not in result.stdout:
            raise EnvironmentError(
                "organoid-analysis conda environment not found"
            )
            
        return True
    except Exception as e:
        logger.error(f"Conda environment check failed: {str(e)}")
        return False

def check_dependencies():
    """检查必要的依赖是否已安装"""
    required_packages = [
        "torch",
        "numpy",
        "scipy",
        "pandas",
        "scikit-image",
        "segment_anything"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
            
    if missing:
        logger.error(f"Missing required packages: {', '.join(missing)}")
        return False
    return True 