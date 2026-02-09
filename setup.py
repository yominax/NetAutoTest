"""
Setup script for NetAutoTest
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="netautotest",
    version="1.0.0",
    author="NetAutoTest Team",
    author_email="team@netautotest.example.com",
    description="Framework DevOps d'automatisation de tests de performance réseau",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/NetAutoTest",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Networking",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.11",
    install_requires=[
        "containernet>=2.3.0",
        "mininet>=2.3.0",
        "iperf3>=0.1.11",
        "scapy>=2.5.0",
        "prometheus-client>=0.19.0",
        "psutil>=5.9.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.0",
        "plotly>=5.17.0",
        "pandas>=2.0.0",
        "pyyaml>=6.0",
        "click>=8.1.0",
        "rich>=13.5.0",
        "loguru>=0.7.0",
        "docker>=6.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "flake8",
            "black",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
            "sphinx-autodoc-typehints>=1.24.0",
            "myst-parser>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "netautotest-sim=src.simulator.network_simulator:main",
            "netautotest-test=src.tests.run_test_campaign:main",
            "netautotest-probe=src.monitoring.probe:main",
        ],
    },
)
