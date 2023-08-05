from distutils.core import setup

setup(
    name='reporter',
    version='0.1.2',
    author='Jeroen Janssens',
    author_email='jeroen.janssens@visualrevenue.com',
    packages=['reporter'],
    url='http://pypi.python.org/pypi/reporter/',
    license='BSD',
    description='Flexible text extraction from HTML in Python.',
    long_description=open('README.md').read(),
    install_requires=[
        "beautifulsoup4 >= 4.1.3",
        "requests >= 0.14.2",
        "lxml >= 3.0.1.",
    ],
)
