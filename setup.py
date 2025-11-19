"""
Setup script for device-activity-telegram-bot.
This is a minimal setup.py for compatibility with tools that require it.
The project is primarily configured via pyproject.toml.
"""
from setuptools import setup

setup(
    py_modules=["halt", "send"],
    packages=[],
    package_dir={"": "src"},
)
