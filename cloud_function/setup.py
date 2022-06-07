import setuptools
from setuptools import find_packages

test_requirements = [
    "pytest",
    "pytest-cov",
    "black",
    "mypy",
]

setuptools.setup(
    name="cloud-function",
    version="0.1.0",
    description="twitter scraper",
    maintainer="Attila Szombati",
    zip_safe=True,
    packages=find_packages(),
    python_requires=">3.7.0, <3.11.0",
    install_requires=[
        "peewee==3.14.4",
        "pandas==1.4.1",
        "snscrape~=0.4.3.20220106",
        "pytest==6.2.4",
        "praw==7.4.0",
        "lint==1.2.1",
        "fastparquet==0.8.1",
        "SQLAlchemy==1.4.35",
        "SQLAlchemy-Utils==0.38.2",
        "pg8000==1.26.1",
        "google-cloud-secret-manager",
        "google-cloud-storage==2.3.0",
        "google-api-python-client==2.45.0",
        "oauth2client==4.1.3",
        "pydantic~=1.9.0",
    ]

)
