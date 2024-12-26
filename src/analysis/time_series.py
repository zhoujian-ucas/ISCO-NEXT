from typing import List, Dict, Any
import numpy as np
from scipy import stats
import pandas as pd
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class TimePoint:
    """时间点数据"""
    time: float  # 时间点
    image: np.ndarray  # 图像数据
    metadata: Dict[str, Any]  # 元数据

class TimeSeriesAnalyzer:
    """时间序列分析器"""
    
    def __init__(self):
        self.time_points: List[TimePoint] = []
        
    def add_time_point(self, time_point: TimePoint):
        """添加时间点数据"""
        self.time_points.append(time_point)
        self._sort_time_points()
        
    def analyze_growth(self) -> Dict[str, Any]:
        """分析生长趋势"""
        try:
            times = [tp.time for tp in self.time_points]
            areas = [tp.metadata.get('area', 0) for tp in self.time_points]
            
            # 计算生长率
            growth_rate = np.diff(areas) / np.diff(times)
            
            # 拟合生长曲线
            slope, intercept, r_value, p_value, std_err = stats.linregress(times, areas)
            
            return {
                'growth_rate': growth_rate.tolist(),
                'average_growth_rate': np.mean(growth_rate),
                'slope': slope,
                'r_squared': r_value**2,
                'p_value': p_value
            }
        except Exception as e:
            logger.error(f"Error analyzing growth: {str(e)}")
            raise
            
    def analyze_morphology_changes(self) -> Dict[str, Any]:
        """分析形态变化"""
        try:
            shape_metrics = []
            for tp in self.time_points:
                metrics = {
                    'time': tp.time,
                    'sphericity': tp.metadata.get('sphericity', 0),
                    'volume': tp.metadata.get('volume', 0),
                    'surface_area': tp.metadata.get('surface_area', 0)
                }
                shape_metrics.append(metrics)
            
            df = pd.DataFrame(shape_metrics)
            
            return {
                'shape_variation': df.std().to_dict(),
                'trend_analysis': self._analyze_trends(df),
                'time_points': df.to_dict('records')
            }
        except Exception as e:
            logger.error(f"Error analyzing morphology changes: {str(e)}")
            raise
            
    def _sort_time_points(self):
        """按时间排序"""
        self.time_points.sort(key=lambda x: x.time)
        
    def _analyze_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """分析时间序列趋势"""
        trends = {}
        for column in df.columns:
            if column != 'time':
                # 计算移动平均
                ma = df[column].rolling(window=3).mean()
                # 计算趋势方向
                trend = 'increasing' if df[column].iloc[-1] > df[column].iloc[0] else 'decreasing'
                trends[column] = {
                    'trend': trend,
                    'moving_average': ma.tolist()
                }
        return trends 