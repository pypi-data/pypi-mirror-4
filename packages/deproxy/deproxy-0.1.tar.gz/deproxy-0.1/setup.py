
from distutils.core import setup

setup(
    name='deproxy',
    version='0.1',
    packages=['deproxy',],
    license='MIT License',
    long_description=open('README.txt').read(),
    author='izrik',
    author_email='izrik@yahoo.com',
    url='https://github.com/izrik/deproxy',
    description='Python library for testing HTTP proxies.',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
)
