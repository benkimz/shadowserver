from setuptools import setup, find_packages

library_description = ""
with open('README.md', 'r', encoding="utf-8") as f:
    library_description = f.read()

setup(
    name='shadowserver',
    version='0.1.9',
    description='An asynchronous HTTP proxy server library using aiohttp, designed to forward requests from clients to a target server',
    long_description=library_description,
    long_description_content_type='text/markdown',
    author='benkimz',
    author_email='benkim3619@gmail.com',
    maintainer='benkimz',
    maintainer_email='benkim3619@gmail.com',
    url='https://github.com/benkimz/shadowserver',
    license='MIT',
    keywords=['proxy', 'server', 'proxy-server', 'http', 'https', 'aiohttp', 'asyncio'],
    platforms=['any'],
    packages=find_packages(),
    install_requires=[
        'aiohttp',
        'multidict',
        'asyncio',
        'Brotli'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)