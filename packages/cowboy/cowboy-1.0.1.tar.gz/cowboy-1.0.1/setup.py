from setuptools import setup
import cowboy

setup(
    name='cowboy',
    version=cowboy.__version__,
    description='Works on ranges',
    url='http://github.com/brianhicks/cowboy',
    author='Brian Hicks',
    author_email='brian@brianthicks.com',
    license='MIT',
    packages=['cowboy'],
    zip_safe=False
)
