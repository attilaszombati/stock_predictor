import setuptools
from setuptools import find_packages

test_requirements = [
    "pytest",
    "pytest-cov",
    "black",
    "mypy",
]

setuptools.setup(
    name="cloud_function",
    version="0.1.0",
    description="twitter scraper",
    maintainer="Attila Szombati",
    zip_safe=True,
    packages=find_packages(),
    python_requires=">3.7.0, <3.11.0",
)
