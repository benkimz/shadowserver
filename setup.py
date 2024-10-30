from setuptools import setup, find_packages


setup(
    name='shadowserver',
    version='0.1.1',
    description='A HTTP/HTTPS proxy server in Python',
    author='Benard K. Wachira',
    packages=find_packages(),
    install_requires=[
        # Dependencies
        'aiohttp',
        'multidict',
        'asyncio'
    ]
)