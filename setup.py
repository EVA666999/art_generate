"""
Setup file for the project.
"""
from setuptools import setup, find_packages

setup(
    name="sd-monitor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "python-telegram-bot>=20.0",
        "loguru>=0.7.0",
        "pydantic-settings>=2.0.0",
        "python-dotenv>=1.0.0",
        "requests>=2.31.0",
    ],
    python_requires=">=3.8",
) 