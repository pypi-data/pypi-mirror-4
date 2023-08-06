
from distutils.core import setup

setup(
    name='froggie',
    version='0.1',
    packages=['froggie',],
    license='MIT License',
    long_description=open('README.txt').read(),
    author='Richard Sartor',
    author_email='richard.sartor@rackspace.com',
    url='https://github.com/richard-sartor/froggie',
    description='Setup scripts for installing atom hopper on a server for automated testing',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
