from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="autonomous-code-archaeology",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Autonomous multi-agent system for analyzing code repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/autonomous-code-archaeology",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "archaeology=archaeology.cli:main",
        ],
    },
    keywords="code analysis architecture refactoring technical-debt quality",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/autonomous-code-archaeology/issues",
        "Source": "https://github.com/yourusername/autonomous-code-archaeology",
        "Documentation": "https://github.com/yourusername/autonomous-code-archaeology#readme",
    },
)
