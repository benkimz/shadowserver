from setuptools import setup, find_packages


setup(
    name='shadowproxy',
    version='0.1.0',
    description='A simple HTTP/HTTPS proxy server in Python',
    author='Benard K. Wachira',
    packages=find_packages(),
    install_requires=[
        # Dependencies
        'aiohttp',
        'multidict',
        'asyncio'
    ]
)