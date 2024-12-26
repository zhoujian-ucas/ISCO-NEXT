from setuptools import setup, find_packages

setup(
    name="organoid-analysis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # 基础依赖会从conda环境获取
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A tool for organoid morphology analysis",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.9",
) 