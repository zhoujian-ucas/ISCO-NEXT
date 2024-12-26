from src.plugin_manager import PluginManager
from src.segmentation_interface import SAMAdapter
from src.morphology_engine import MorphologyEngine
from src.visualization_platform import VisualizationPlatform
from src.plugins.spheroid_plugin import SpheroidPlugin
from src.utils.logger import setup_logger
from src.utils.exporter import ResultExporter
from src.config import Config
from pathlib import Path
import logging
import yaml
from src.utils.performance import ProcessingPool, GPUAccelerator, DataCache
import torch
from src.analysis.time_series import TimeSeriesAnalyzer, TimePoint

def process_image(args):
    """处理单个图像的函数"""
    img_path, config, gpu_acc = args
    
    # 加载图像
    image = load_image(img_path)
    
    # GPU加速处理
    if gpu_acc.is_gpu_available:
        image_tensor = gpu_acc.to_device(image)
        # 执行GPU加速的操作
        result_tensor = process_on_gpu(image_tensor)
        image = gpu_acc.to_numpy(result_tensor)
    
    return {
        'path': str(img_path),
        'result': image
    }

def analyze_time_series(image_dir: Path, config: Config):
    """分析时间序列数据"""
    try:
        # 初始化分析器
        time_series_analyzer = TimeSeriesAnalyzer()
        
        # 获取所有时间点的图像
        image_files = sorted(image_dir.glob('*.tif'))
        
        # 处理每个时间点
        for img_file in image_files:
            # 从文件名提取时间信息
            time_point = float(img_file.stem.split('_')[1])  # 假设文件名格式为 "image_timepoint.tif"
            
            # 处理图像
            image = load_image(img_file)
            mask = segmentation_model.segment(image)
            
            # 分析形态
            analysis_results = spheroid_plugin.analyze(mask)
            morphology_results = morphology_engine.calculate_2d_features(mask)
            
            # 创建时间点数据
            time_point_data = TimePoint(
                time=time_point,
                image=image,
                metadata={**analysis_results, **morphology_results}
            )
            
            # 添加到时间序列
            time_series_analyzer.add_time_point(time_point_data)
        
        # 分析时间序列
        growth_analysis = time_series_analyzer.analyze_growth()
        morphology_changes = time_series_analyzer.analyze_morphology_changes()
        
        # 导出结果
        time_series_results = {
            'growth_analysis': growth_analysis,
            'morphology_changes': morphology_changes,
            'time_points': [tp.metadata for tp in time_series_analyzer.time_points]
        }
        
        exporter.export_time_series(time_series_results, 'time_series_analysis')
        
        logger.info("Time series analysis completed successfully")
        
    except Exception as e:
        logger.error(f"Time series analysis failed: {str(e)}")
        raise

def main():
    # 检查CUDA可用性
    if torch.cuda.is_available():
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA is not available, using CPU")
    
    # 加载配置
    config = Config.from_yaml('config.yaml')
    
    # 根据CUDA可用性设置设备
    if torch.cuda.is_available() and config.performance.gpu_enabled:
        device = torch.device('cuda')
        # 设置GPU内存使用限制
        torch.cuda.set_per_process_memory_fraction(
            config.performance.gpu_memory_fraction
        )
    else:
        device = torch.device('cpu')
    
    # 初始化性能优化组件
    processing_pool = ProcessingPool(
        num_workers=config.performance.num_workers
    )
    gpu_acc = GPUAccelerator(device=str(device))
    data_cache = DataCache(
        cache_dir=config.performance.cache_dir,
        max_size=config.performance.cache_size
    )
    
    # 设置日志
    logger = setup_logger('organoid_analysis', 
                         config.output_dir / 'analysis.log',
                         level=getattr(logging, config.log_level.upper()))
    
    try:
        # 初始化插件系统
        plugin_manager = PluginManager()
        plugin_manager.load_plugins(Path("src/plugins"))
        
        # 加载插件配置
        with open("config/plugins/spheroid.yaml") as f:
            plugin_config = yaml.safe_load(f)
        
        # 创建插件实例
        spheroid_plugin = plugin_manager.create_plugin(
            plugin_type="organoid",
            plugin_name="spheroid",
            config=plugin_config["config"]
        )
        
        # 初始化系统
        segmentation_model = SAMAdapter(config.model_path)
        morphology_engine = MorphologyEngine()
        vis_platform = VisualizationPlatform()
        exporter = ResultExporter(config.output_dir)
        
        # 准备批处理参数
        image_paths = list(Path('data').glob('*.tif'))
        process_args = [(p, config, gpu_acc) for p in image_paths]
        
        # 使用多进程池处理图像
        results = processing_pool.map_batch(
            process_image, 
            process_args,
            batch_size=config.batch_size
        )
        
        # 处理结果
        for result in results:
            if result is None:
                continue
                
            img_path = result['path']
            image = result['result']
            
            # 使用缓存加速重复计算
            cache_key = f"analysis_{img_path}"
            analysis_results = data_cache.get_cached(cache_key)
            
            if analysis_results is None:
                # 执行分析
                mask = segmentation_model.segment(image)
                analysis_results = spheroid_plugin.analyze(mask)
                morphology_results = morphology_engine.calculate_2d_features(mask)
                
                # 缓存结果
                combined_results = {
                    'image_path': img_path,
                    **analysis_results,
                    **morphology_results
                }
                data_cache.cache_result(cache_key, combined_results)
            
            # 添加到结果列表
            results.append(analysis_results)
        
        # 导出结果
        exporter.export_to_csv(results, 'analysis_results')
        exporter.export_to_json(results, 'analysis_results')
        exporter.save_figures(figures)
        
        logger.info("Analysis completed successfully")
        
        # 处理单个时间点的图像
        process_single_timepoint(config)
        
        # 处理时间序列数据
        if config.time_series_enabled:
            analyze_time_series(Path(config.time_series_dir), config)
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise

if __name__ == '__main__':
    main() 