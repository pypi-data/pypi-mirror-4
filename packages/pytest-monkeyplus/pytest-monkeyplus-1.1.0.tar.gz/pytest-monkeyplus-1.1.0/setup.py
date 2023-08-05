from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3',
]

LONG_DESC = open('README', 'rt').read() + '\n\n' + open('CHANGES', 'rt').read()

setup(
    name='pytest-monkeyplus',
    description="pytest's monkeypatch subclass with extra functionalities",
    long_description=LONG_DESC,
    classifiers=CLASSIFIERS,
    version='1.1.0',
    author='Virgil Dupras',
    author_email='hsoft@hardcoded.net',
    url='http://bitbucket.org/hsoft/pytest-monkeyplus/',
    py_modules=['pytest_monkeyplus'],
    entry_points={'pytest11': ['monkeyplus = pytest_monkeyplus']},
    install_requires=['pytest>=2.0'],
)