from distutils.core import setup

setup(
    name='FSGDeploy',
    version='0.2.4',
    author='FSG',
    author_email='dweiss@frontierstrategygroup.com',
    packages=['FSGDeploy'],
    url='http://pypi.python.org/pypi/FSGDeploy/',
    license='LICENSE.txt',
    description='Universal website deploy script.',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
    entry_points = {
        'console_scripts':
            ['deploy = FSGDeploy.deploy:main'],
    }
)
