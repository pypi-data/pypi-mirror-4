from setuptools import setup


with open("README") as file:
    long_description = file.read()

setup(
    name="FoneAstra",
    version="3.0.1",
    license="BSD",
    long_description=long_description,

    install_requires = [
        "django",
        "django-nose",
        "djtables",
        "djappsettings",
        "django-celery",
        "South",
        "supervisor",
    ],

    packages = ['fa'],
    include_package_data = True,

    author="University of Washington CSE",
    author_email="pittsw@uw.edu",

    maintainer="University of Washington CSE",
    maintainer_email="pittsw@uw.edu",

    description="Django package necessary for running a FoneAstra server.",
    url="https://bitbucket.org/pittsw/foneastra-base",
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Healthcare Industry",
    ],
)
