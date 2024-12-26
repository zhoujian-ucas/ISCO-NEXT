import numpy as np
from typing import Dict, Any, List
from skimage import measure, morphology
from scipy import ndimage
import logging
import torch

logger = logging.getLogger(__name__)

class MorphologyEngine:
    """支持GPU加速的形态学分析引擎"""
    
    def __init__(self, gpu_acc: GPUAccelerator = None):
        self.measurements = {}
        self.gpu_acc = gpu_acc or GPUAccelerator()
        
    def calculate_2d_features(self, mask: np.ndarray) -> Dict[str, Any]:
        """计算2D形态特征（支持GPU加速）"""
        try:
            if self.gpu_acc.is_gpu_available:
                # 转换为GPU张量
                mask_tensor = self.gpu_acc.to_device(mask)
                
                # GPU加速的形态学计算
                props = self._calculate_props_gpu(mask_tensor)
                
                # 转换回CPU
                props = self._tensor_to_props(props)
            else:
                props = measure.regionprops(mask.astype(int))[0]
            
            # 添加更多形态学特征
            features = {
                'area': props.area,
                'perimeter': props.perimeter,
                'eccentricity': props.eccentricity,
                'solidity': props.solidity,
                'major_axis_length': props.major_axis_length,
                'minor_axis_length': props.minor_axis_length,
                'orientation': props.orientation,
                'circularity': 4 * np.pi * props.area / (props.perimeter ** 2),
                'aspect_ratio': props.major_axis_length / props.minor_axis_length
            }
            
            # 添加纹理特征
            features.update(self._calculate_texture_features(mask))
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating 2D features: {str(e)}")
            raise
            
    def calculate_3d_features(self, volume: np.ndarray) -> Dict[str, Any]:
        """计算3D形态特征"""
        try:
            props = measure.regionprops(volume.astype(int))[0]
            
            features = {
                'volume': props.area,
                'surface_area': self._calculate_surface_area(volume),
                'sphericity': self._calculate_sphericity(volume),
                'compactness': self._calculate_compactness(volume),
                'principal_moments': props.inertia_tensor_eigvals,
                'elongation': self._calculate_elongation(props)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error calculating 3D features: {str(e)}")
            raise
            
    def batch_process(self, images: List[np.ndarray]) -> List[Dict[str, Any]]:
        """批量处理多个图像"""
        results = []
        for idx, image in enumerate(images):
            try:
                if image.ndim == 2:
                    result = self.calculate_2d_features(image)
                else:
                    result = self.calculate_3d_features(image)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing image {idx}: {str(e)}")
                results.append(None)
        return results
    
    def _calculate_texture_features(self, mask: np.ndarray) -> Dict[str, float]:
        """计算纹理特征"""
        glcm = morphology.local_binary_pattern(mask, 8, 1)
        return {
            'texture_uniformity': np.sum(glcm ** 2),
            'texture_entropy': -np.sum(glcm * np.log2(glcm + 1e-10))
        } 
    
    def _calculate_props_gpu(self, mask_tensor: torch.Tensor):
        """在GPU上计算区域属性"""
        # 实现GPU加速的形态学计算
        # 这里可以使用torch.cuda操作进行加速
        pass 