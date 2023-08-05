from distutils.core import setup

setup(
    name='reporter',
    version='0.1.0',
    author='Jeroen Janssens',
    author_email='jeroen.janssens@visualrevenue.com',
    packages=['reporter'],
    url='http://pypi.python.org/pypi/reporter/',
    license='LICENSE',
    description='Flexible text extraction from HTML in Python.',
    long_description=open('README.md').read(),
    install_requires=[
        "beautifulsoup4 >= 4.1.3",
    ],
)
