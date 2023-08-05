from distutils.core import setup

setup(
    name='storage',
    version='0.0.2',
    author='Srikanth Chundi',
    author_email='srikanth912@gmail.com',
    packages=['storage', 'storage.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/storage/',
    license='LICENSE.txt',
    description='Libraries to interact with devices in SAN/NAS infrastructure.',
    long_description=open('README.txt').read(),
    install_requires=[
        "paramiko >= 1.8.0",
        ],
)