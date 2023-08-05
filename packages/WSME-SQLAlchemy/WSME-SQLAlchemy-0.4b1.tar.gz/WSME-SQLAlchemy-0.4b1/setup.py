from setuptools import setup

setup(
    name='WSME-SQLAlchemy',
    version='0.4b1',
    description='SQLAlchemy support for WSME',
    long_description='''
SQLAlchemy support for WSME (http://pypi.python.org/pypi/WSME).
    ''',
    author='Christophe de Vienne',
    author_email='cdevienne@gmail.com',
    url='http://pypi.python.org/pypi/WSME',
    namespace_packages=['wsmeext'],
    packages=['wsmeext', 'wsmeext.sqlalchemy',
        'wsmeext.sqlalchemy.tests'],
    install_requires=[
        'WSME',
        'SQLAlchemy >= 0.5.8'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
