from setuptools import setup, find_packages

library_description = ""
with open('README.md', 'r', encoding="utf-8") as f:
    library_description = f.read()

setup(
    name='shadowserver',
    version='0.1.7',
    description='An asynchronous HTTP/HTTPS proxy server library built using aiohttp',
    long_description=library_description,
    long_description_content_type='text/markdown',
    author='Benard K. Wachira (@benkimz)',
    maintainer='@benkimz',
    url='https://github.com/benkimz/shadowserver',
    license='MIT',
    keywords=['proxy', 'server', 'proxy-server', 'http', 'https', 'aiohttp', 'asyncio'],
    platforms=['any'],
    packages=find_packages(),
    install_requires=[
        # Dependencies
        'aiohttp',
        'multidict',
        'asyncio',
        'Brotli'
    ]
)