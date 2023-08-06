from distutils.core import setup

setup(
    name='qThread',
    version='0.1.0',
    author='Adam Lewis',
    author_email='aclewis182@gmail.com',
    packages=['qthread', ],
    scripts=[],
    url='http://pypi.python.org/pypi/qThread/',
    license='LICENSE.txt',
    description='Generic stoppable thread',
    long_description=open('README.txt').read(),
    install_requires=[],
)
