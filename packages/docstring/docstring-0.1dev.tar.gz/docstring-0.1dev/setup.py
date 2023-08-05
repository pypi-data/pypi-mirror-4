from distutils.core import setup

requires = []

setup(
    author='Eytan Daniyalzade',
    author_email='eytan@chartbeat.com',
    url='http://chartbeat.com',
    name='docstring',
    version='0.1dev',
    packages=['docstring',],
    license='Decorators for auto-generating HTML response for API endpoints',
    long_description=open('README.rst').read(),
    install_requires=requires,
)
