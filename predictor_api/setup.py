import setuptools
from setuptools import find_packages

test_requirements = [
    "pytest",
    "pytest-cov",
    "black",
    "mypy",
]

setuptools.setup(
    name="predictor-api",
    version="0.1.0",
    description="predictor api",
    maintainer="Attila Szombati",
    zip_safe=True,
    packages=find_packages(),
    python_requires=">3.7.0, <3.11.0",
    install_requires=[
        "sklearn",
        "tensorflow",
        "numpy==1.23.3",
        "google-cloud-storage==2.3.0",
        "google-api-python-client==2.45.0",
        "oauth2client==4.1.3",
        "gunicorn==20.1.0",
        "Flask==2.1.2",
        "google-cloud-bigquery==3.3.6",
        "pandas==1.4.1",
        "db-dtypes==1.0.4",
        "black==22.10.0",
        "alpaca-trade-api==2.3.0",
        "alpaca-py==0.6.0",
        "lint==1.2.1"
    ],
)
