from setuptools import setup, find_packages

setup(
    name='aweber_api',
    version='1.1.3',
    packages=find_packages(exclude=['tests']),
    url='https://github.com/aweber/AWeber-API-Python-Library',
    install_requires = [
        'httplib2>=0.7.0',
        'oauth2>=1.2',
        ],
    tests_require = [
        'dingus',
        'coverage',
        ],
    setup_requires = [
        'nose',
        ],
    include_package_data=True
)

