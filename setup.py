from setuptools import setup, find_packages

setup(
    name='pymicrohttp',
    version='0.1.1',
    packages=find_packages(),
    description='Tiny lightweight, flexible HTTP framework.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Hassan Ezz',
    author_email='dhassanezz@gmail.com',
    url='https://github.com/hasssanezzz/PyMicroHTTP',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
