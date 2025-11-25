from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Read README for long description
try:
    with open('README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = "DevOps interface for Belgrano Ahorro"

setup(
    name="belgrano_devops",
    version=os.getenv('VERSION', '0.1.0'),
    packages=find_packages(include=['devops', 'devops.*']),
    include_package_data=True,
    package_data={
        'devops': ['templates/*', 'static/*', '*.env'],
    },
    install_requires=required,
    python_requires='>=3.8',
    author="Belgrano Ahorro Team",
    author_email="dev@belgranoahorro.com",
    description="DevOps interface for Belgrano Ahorro",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/chubus/devops",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={
        'console_scripts': [
            'belgrano-devops=devops.cli:main',
        ],
    },
)
