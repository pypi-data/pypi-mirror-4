from setuptools import setup, find_packages

setup(
    name='PythonExacttarget',
    version='0.1.0',
    author='Matthew Black',
    author_email='consult@jbadigital.com',
    url='https://github.com/damilare/pythonexacttarget/',
    packages=find_packages(),
    install_requires=['suds'],
    license='LICENSE.txt',
    description='Python Wrapper for Exact Target SOAP API',
    long_description='Python Wrapper for Exact Target SOAP API',
    dependency_links = ['https://github.com/damilare/pythonexacttarget/archive/v0.1.0.tar.gz']
)
