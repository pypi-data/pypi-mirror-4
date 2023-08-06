from distutils.core import setup

setup(
    name='spiderman',
    version='0.1.0',
    author='J. Random Hacker',
    author_email='jrh@k17.org',
    packages=['spiderman'],
    scripts=[],
    url='http://pypi.python.org/pypi/spiderman/',
    license='LICENSE.txt',
    description='A wrapper around web.py to make it more like sinatra.',
    long_description=open('README.txt').read(),
    install_requires=["web.py", "PyHAML"],
)
