from setuptools import find_packages,setup

def get_requirements():

    with open("requirements.txt") as f:
        requirements=f.readlines()

    requirements_list=[package.replace("\n","") for package in requirements if package !='-e .']
    return requirements_list

setup(
    name='HouseRentPrediction',
    version='0.0.1',
    author='Techner',
    author_email='k.balamurali303@gmail.com',
    install_requires=get_requirements(),
    packages=find_packages()
)