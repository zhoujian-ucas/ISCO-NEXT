from typing import List, Callable, Any
import multiprocessing as mp
from pathlib import Path
import numpy as np
import torch
from functools import lru_cache
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ProcessingPool:
    """多进程处理池"""
    
    def __init__(self, num_workers: int = None):
        self.num_workers = num_workers or mp.cpu_count()
        
    def map_batch(self, func: Callable, items: List[Any], 
                 batch_size: int = 1) -> List[Any]:
        """批量处理数据"""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            # 提交批处理任务
            futures = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                future = executor.submit(self._process_batch, func, batch)
                futures.append(future)
            
            # 收集结果
            for future in as_completed(futures):
                try:
                    batch_result = future.result()
                    results.extend(batch_result)
                except Exception as e:
                    logger.error(f"Batch processing error: {str(e)}")
                    
        return results
    
    @staticmethod
    def _process_batch(func: Callable, batch: List[Any]) -> List[Any]:
        """处理单个批次"""
        return [func(item) for item in batch]

class GPUAccelerator:
    """GPU加速器"""
    
    def __init__(self, device: str = None):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.torch_enabled = self.device != 'cpu'
        
    def to_device(self, data: np.ndarray) -> torch.Tensor:
        """将数据转移到GPU"""
        if self.torch_enabled:
            return torch.from_numpy(data).to(self.device)
        return data
    
    def to_numpy(self, tensor: torch.Tensor) -> np.ndarray:
        """将数据转回CPU"""
        if self.torch_enabled:
            return tensor.cpu().numpy()
        return tensor
    
    @property
    def is_gpu_available(self) -> bool:
        return self.torch_enabled

class DataCache:
    """数据缓存管理器"""
    
    def __init__(self, cache_dir: Path = None, max_size: int = 1000):
        self.cache_dir = cache_dir or Path(".cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size = max_size
        
    @lru_cache(maxsize=1000)
    def cache_result(self, key: str, value: Any) -> Any:
        """缓存计算结果"""
        return value
    
    def get_cached(self, key: str) -> Any:
        """获取缓存结果"""
        try:
            return self.cache_result(key, None)
        except Exception:
            return None 