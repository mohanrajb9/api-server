"""Setup script for the api-ser package."""

from setuptools import setup, find_packages

setup(
    name="api-ser",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
