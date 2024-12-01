from setuptools import setup, find_packages

setup(
    name="portfolio",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "pyyaml>=5.4.1",
        "pydantic>=1.8.2",
    ],
)
