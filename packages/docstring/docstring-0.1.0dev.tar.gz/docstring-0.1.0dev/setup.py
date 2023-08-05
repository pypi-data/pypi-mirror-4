from distutils.core import setup

requires = []

packages = [
    'docstring',
]

setup(
    name='docstring',
    author='Eytan Daniyalzade',
    author_email='eytan@chartbeat.com',
    url='http://chartbeat.com',
    packages=packages,
    description='Decorators for auto-generating HTML response for API endpoints',
    long_description=open('README.rst').read(),
    version='0.1.0dev',
    data_files=[('', ['README.rst', 'LICENSE'])],
    license=open('LICENSE').read(),
    install_requires=requires,
    include_package_data=True,
)
