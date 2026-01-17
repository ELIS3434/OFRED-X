from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="antibot-response-manager",
    version="1.0.0",
    author="Your Name",
    description="Advanced Anti-Bot Response System for Reddit & OnlyFans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/AntiBot-Response-Manager",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    python_requires=">=3.10",
    install_requires=[
        "customtkinter>=5.2.0",
        "praw>=7.8.0",
        "openai>=1.3.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "python-dotenv>=1.0.0",
    ],
)
