from setuptools import setup

CLASSIFIERS = [
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
]

LONG_DESC = open('README', 'rt').read() + '\n\n' + open('CHANGES', 'rt').read()

setup(
    name='objp',
    version='1.3.0',
    author='Hardcoded Software',
    author_email='hsoft@hardcoded.net',
    packages=['objp'],
    package_data={'objp': ['data/*']},
    scripts=[],
    install_requires=[],
    url='http://hg.hardcoded.net/objp/',
    license='BSD License',
    description='Python<-->Objective-C bridge with a code generation approach',
    long_description=LONG_DESC,
    classifiers=CLASSIFIERS,
)
