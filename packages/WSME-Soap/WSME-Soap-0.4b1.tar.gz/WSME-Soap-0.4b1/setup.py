from setuptools import setup

setup(
    name='WSME-Soap',
    version='0.4b1',
    description='Soap support for WSME',
    long_description='''
SOAP implementation for WSME (http://pypi.python.org/pypi/WSME).
    ''',
    author='Christophe de Vienne',
    author_email='cdevienne@gmail.com',
    url='http://pypi.python.org/pypi/WSME',
    namespace_packages=['wsmeext'],
    packages=['wsmeext', 'wsmeext.soap'],
    package_data={
        'wsmeext.soap': ['*.html']
    },
    install_requires=[
        'WSME',
        'Genshi',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    entry_points={
        'wsme.protocols': [
            'soap = wsmeext.soap:SoapProtocol',
        ]
    },
)
