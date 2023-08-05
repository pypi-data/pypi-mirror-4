from setuptools import setup

setup(
    name='WSME-ExtDirect',
    version='0.4b1',
    description='ExtDirect support for WSME',
    long_description='''
ExtDirect (http://www.sencha.com/products/extjs/extdirect)
implementation for WSME (http://pypi.python.org/pypi/WSME).
    ''',
    author='Christophe de Vienne',
    author_email='cdevienne@gmail.com',
    url='http://pypi.python.org/pypi/WSME',
    namespace_packages=['wsmeext'],
    packages=['wsmeext', 'wsmeext.extdirect'],
    install_requires=[
        'WSME',
        'WSME-SQLAlchemy',
        'Mako',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    entry_points={
        'wsme.protocols': [
            'extdirect = wsmeext.extdirect:ExtDirectProtocol',
        ]
    },
)
