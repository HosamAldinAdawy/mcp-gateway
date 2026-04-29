from setuptools import setup, find_packages
import os

# Read long description
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="mcp-gateway",
    version="1.0.0",
    description="Secure remote MCP gateway — auth, audit, registry, and SSE transport in one command",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Hosam Aldin Adawy",
    url="https://github.com/HosamAldinAdawy/mcp-gateway",
    license="MIT",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
    ],
    keywords="mcp llm gateway claude security ai-tools",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    package_data={
        "mcp_gateway": [
            "*.json",
            "*.env.example",
            "templates/**/*.py",
            "security/policy.json",
            "registry/registry.json",
            "scripts/*.sh",
            "infra/*",
        ],
    },
    include_package_data=True,
    install_requires=[
        "fastapi==0.115.0",
        "uvicorn[standard]==0.30.0",
        "httpx==0.27.0",
        "pydantic==2.8.0",
        "python-dotenv==1.0.1",
        "sse-starlette==2.1.3",
        "anyio==4.4.0",
        "aiofiles==23.2.1",
    ],
    entry_points={
        "console_scripts": [
            "mcp-gateway=mcp_gateway.cli_entry:main",
        ],
    },
    project_urls={
        "Homepage": "https://github.com/HosamAldinAdawy/mcp-gateway",
        "Issues": "https://github.com/HosamAldinAdawy/mcp-gateway/issues",
    },
)
