from setuptools import setup, find_packages

setup(
    name="reconforge",
    version="1.0.0",
    author="ReconForge Security Team",
    author_email="team@reconforge.local",
    url="https://github.com/harpalsinh070/reconxforge",
    description="Linux Reconnaissance & Attack Surface Management Tool",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "click>=8.1.7",
        "rich>=13.7.1",
        "httpx>=0.27.0",
        "dnspython>=2.6.1",
        "beautifulsoup4>=4.12.3",
        "sqlalchemy>=2.0.28",
        "aiosqlite>=0.20.0",
        "greenlet>=3.0.0",
        "jinja2>=3.1.3",
        "pyyaml>=6.0.1"
    ],
    entry_points={
        "console_scripts": [
            "reconforge=reconforge.cli:cli"
        ]
    },
    classifiers=[
        "Environment :: Console",
        "Operating System :: POSIX :: Linux",
        "Topic :: Security",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12"
    ]
)
