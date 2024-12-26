# 类器官形态分析工具

## 项目概述

类器官形态分析工具是一个模块化的平台，专为生物学研究人员设计，用于分析类器官的二维和三维形态结构。该工具支持多种分割模型（如SAM和DINO），并通过插件架构实现形态学定义和分析。最终结果可以通过可视化平台进行展示，帮助研究人员更好地理解类器官的生长和形态变化。

## 功能特性

- **插件架构**：支持自定义插件，便于扩展形态学分析功能。用户可以根据研究需求开发新的插件。
- **多模型支持**：集成多种分割模型，灵活选择，适应不同的图像数据和分析需求。
- **性能优化**：支持多进程处理、GPU加速和数据缓存，提升大规模数据集的处理效率。
- **时间序列分析**：分析类器官的生长趋势和形态变化，提供详细的统计分析和可视化。
- **结果导出**：支持CSV、JSON格式导出和图形保存，便于数据共享和进一步分析。

## 安装

1. 克隆项目仓库：

   ```bash
   git clone https://github.com/yourusername/organoid-analysis-tool.git
   cd organoid-analysis-tool
   ```

2. 选择以下任一方式创建环境：

    使用 pip：
    ```bash
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

    或使用 Conda：
    ```bash
    conda env create -f environment.yml
    conda activate organoid-analysis
    ```

3. 验证安装：
    ```bash
    python -c "import torch; print(f'PyTorch version: {torch.__version__}')"
    python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
    ```

## 使用说明

1. 配置项目：

   - 编辑 `config.yaml` 文件，设置模型路径、输出目录、批处理参数等。
   - 配置插件参数，编辑 `config/plugins/spheroid.yaml` 等插件配置文件。

2. 运行分析：

   ```bash
   python examples/usage.py
   ```

3. 查看结果：

   - 分析结果将保存在配置文件中指定的输出目录中。
   - 时间序列分析结果将以CSV和JSON格式导出，并生成相关图表。

## 目录结构

```
.
├── config/                 # 配置文件
├── data/                   # 输入数据
├── examples/               # 使用示例
├── src/                    # 源代码
│   ├── analysis/           # 分析模块
│   ├── plugins/            # 插件模块
│   ├── utils/              # 工具模块
│   └── ...                 # 其他模块
└── README.md               # 项目说明
```

## 贡献指南

欢迎对本项目进行贡献！请遵循以下步骤：

1. Fork 本仓库。
2. 创建一个新的分支：`git checkout -b feature/your-feature-name`
3. 提交更改：`git commit -m 'Add some feature'`
4. 推送到分支：`git push origin feature/your-feature-name`
5. 创建一个 Pull Request。

## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 支持

如果您在使用过程中遇到问题，或者有任何建议，请通过 [GitHub Issues](https://github.com/yourusername/organoid-analysis-tool/issues) 联系我们。

## 参考文献

- [Organoid Research](https://www.nature.com/subjects/organoids)
- [Image Segmentation Models](https://arxiv.org/abs/2003.10580) 