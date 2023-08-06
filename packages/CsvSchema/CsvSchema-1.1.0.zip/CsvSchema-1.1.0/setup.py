from distutils.core import setup


long_description = ''
try:
    long_description = open('README.rst', 'rt').read()
except IOError:
    pass


setup(
    name='CsvSchema',
    version='1.1.0',
    author='Piotr Olejarz',
    author_email='vadwook@hotmail.com',
    url='http://bitbucket.org/vadwook/csvschema/',
    packages=['csv_schema', 'csv_schema.columns', 'csv_schema.structure'],
    license='LICENSE.txt',
    description='Module for describing CSV data structure.',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Text Processing',
    ],
)
