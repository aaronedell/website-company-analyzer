from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="website-company-analyzer",
    version="1.0.0",
    author="Aaron Edell",
    author_email="aaronedell@gmail.com",
    description="A CLI tool that analyzes company websites and generates executive summaries using AWS Bedrock",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aaronedell/website-company-analyzer",
    py_modules=["analyzer"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Researchers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "website-analyzer=analyzer:main",
        ],
    },
)
