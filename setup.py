from setuptools import setup, find_packages

setup(
    name="linkpulse-backend",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "pytest",
        "httpx",
        "pytest-asyncio",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
    ],
) 