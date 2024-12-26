from typing import Dict, Any
import pandas as pd
import json
from pathlib import Path
import matplotlib.pyplot as plt
import logging

logger = logging.getLogger(__name__)

class ResultExporter:
    """增强的结果导出工具"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def export_to_csv(self, results: List[Dict[str, Any]], filename: str):
        """导出为CSV文件"""
        try:
            df = pd.DataFrame(results)
            output_path = self.output_dir / f"{filename}.csv"
            df.to_csv(output_path, index=False)
            logger.info(f"Results exported to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            
    def export_to_json(self, results: Dict[str, Any], filename: str):
        """导出为JSON文件"""
        try:
            output_path = self.output_dir / f"{filename}.json"
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            logger.info(f"Results exported to {output_path}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {str(e)}")
            
    def save_figures(self, figures: Dict[str, plt.Figure]):
        """保存matplotlib图形"""
        try:
            for name, fig in figures.items():
                output_path = self.output_dir / f"{name}.png"
                fig.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close(fig)
            logger.info(f"Figures saved to {self.output_dir}")
        except Exception as e:
            logger.error(f"Error saving figures: {str(e)}")
            
    def export_time_series(self, time_series_data: Dict[str, Any], filename: str):
        """导出时间序列数据"""
        try:
            # 导出为CSV
            df = pd.DataFrame(time_series_data['time_points'])
            csv_path = self.output_dir / f"{filename}_timeseries.csv"
            df.to_csv(csv_path, index=False)
            
            # 导出分析结果
            analysis_path = self.output_dir / f"{filename}_analysis.json"
            analysis_results = {
                'growth_analysis': time_series_data.get('growth_analysis', {}),
                'morphology_changes': time_series_data.get('morphology_changes', {})
            }
            with open(analysis_path, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            
            # 生成时间序列图表
            self._plot_time_series(time_series_data, filename)
            
            logger.info(f"Time series data exported to {self.output_dir}")
            
        except Exception as e:
            logger.error(f"Error exporting time series data: {str(e)}")
            
    def _plot_time_series(self, data: Dict[str, Any], filename: str):
        """绘制时间序列图表"""
        try:
            df = pd.DataFrame(data['time_points'])
            
            # 创建多子图
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            
            # 绘制生长曲线
            axes[0,0].plot(df['time'], df['volume'], 'b-')
            axes[0,0].set_title('Growth Curve')
            axes[0,0].set_xlabel('Time')
            axes[0,0].set_ylabel('Volume')
            
            # 绘制形态变化
            axes[0,1].plot(df['time'], df['sphericity'], 'r-')
            axes[0,1].set_title('Morphology Changes')
            axes[0,1].set_xlabel('Time')
            axes[0,1].set_ylabel('Sphericity')
            
            # 绘制生长率
            if 'growth_analysis' in data:
                growth_rate = data['growth_analysis']['growth_rate']
                axes[1,0].plot(df['time'][1:], growth_rate, 'g-')
                axes[1,0].set_title('Growth Rate')
                axes[1,0].set_xlabel('Time')
                axes[1,0].set_ylabel('Growth Rate')
            
            # 保存图表
            plot_path = self.output_dir / f"{filename}_timeseries_plots.png"
            plt.savefig(plot_path, dpi=300, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            logger.error(f"Error plotting time series: {str(e)}") 