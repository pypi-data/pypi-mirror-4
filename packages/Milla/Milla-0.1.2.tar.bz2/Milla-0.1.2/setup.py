import sys
try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

install_requires = [
    'WebOb',
]

if sys.version_info < (2, 7):
    install_requires.append('ArgParse')

setup(
    name='Milla',
    version='0.1.2',
    description='Lightweight WSGI framework for web applications',
    long_description='''\
Milla is a simple WSGI framework for Python web applications. It is mostly
an exercise to familiarize myself with WSGI, but may evolve into a framework
I use for web applications in the future.
''',
    author='Dustin C. Hatch',
    author_email='admiralnemo@gmail.com',
    url='http://bitbucket.org/AdmiralNemo/milla',
    license='APACHE-2',
    classifiers=[
         'Development Status :: 3 - Alpha',
         'Environment :: Web Environment',
         'Intended Audience :: Developers',
         'License :: OSI Approved :: Apache Software License',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7',
         'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    install_requires=install_requires,
    packages=find_packages('src', exclude=['distribute_setup']),
    package_dir={'': 'src'},
    package_data={
        'milla': ['milla.ico'],
    },
    entry_points={
        'milla.request_validator': [
            'default = milla.auth:RequestValidator'
        ],
        'console_scripts': [
            'milla-cli = milla.cli:main'
        ],
    }
)
