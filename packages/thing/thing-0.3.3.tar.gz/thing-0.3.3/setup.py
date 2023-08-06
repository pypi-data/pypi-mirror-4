from setuptools import setup
import os
import sys
import thing

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name = thing.__name__,
    version = thing.__version__,
    url = 'http://github.com/lzyy/thing',
    license = thing.__license__,
    author = thing.__author__,
    author_email = 'healdream@gmail.com',
    description = 'lightweight SQLAlchemy based ORM',
    long_description = open('README.md').read(),
    zip_safe = False,
    platforms = 'any',
    packages = ["thing"],
    include_package_data = True,
    install_requires = [
        'sqlalchemy',
        'mysql-python',
    ],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
