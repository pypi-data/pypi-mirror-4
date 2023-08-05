from distutils.core import setup

setup(
    name='ExamplePackage',
    version='0.1.0',
    author='Chaithra M V',
    author_email='chaithra_mv@spanservices.com',
    packages=['ExamplePackage','ExamplePackage.SubPackage1', 'ExamplePackage.SubPackage2','ExamplePackage.SubPackage2.GrandPackage'],
    scripts=[''],
    url='http://pypi.python.org/pypi/ExamplePackage/',
    license='LICENSE.txt',
    description='An example package',
    long_description=open('README.txt').read(),
    install_requires=[
        "Python >= 2.7"
    ],
)