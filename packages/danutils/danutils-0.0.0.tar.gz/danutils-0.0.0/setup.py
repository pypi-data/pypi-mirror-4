from setuptools import setup

subs = 'cuda do img lib misc pandatools sci wx'.split(' ')
subpackages = ['danutils.'+x for x in subs]

setup(
    name='danutils',
    version='0.0.0',
    packages=['danutils'] + subpackages,
    license='BSD',
    long_description=open('README.rst').read(),
)
