from distutils.core import setup

setup (
name='ec2spot',
version='0.1.0',
author='Dinesh P. Weerapurage',
author_email='xydinesh@gmail.com',
packages=['ec2spot'],
scripts=['bin/fabfile.py'],
url='http://pypi.python.org/pypi/EC2Spot',
license='LICENSE.txt',
long_description=open('README.md').read(),
install_requires=[
"boto == 2.6.0",
],
)
