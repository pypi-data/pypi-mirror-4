from distutils.core import setup

setup(
    name='storage',
    version='0.0.4.1',
    author='Srikanth Chundi',
    author_email='srikanth912@gmail.com',
    packages=['storage', 'storage.test'],
    scripts=[],
    url='http://docs.enterprisestorage.in/en/latest/',
    download_url='http://pypi.python.org/pypi/storage/',
    license='LICENSE.txt',
    description='Libraries to interact with Enterprise Storage Arrays, FC Switches and Servers.',
    long_description=open('README.txt').read(),
    install_requires=[
        "paramiko >= 1.8.0",
        ],
)