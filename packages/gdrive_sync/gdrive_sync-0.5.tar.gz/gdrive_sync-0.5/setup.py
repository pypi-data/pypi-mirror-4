from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name = 'gdrive_sync',
    packages = ['gdrive_sync'],
    version = '0.5',
    description = 'Sync directories between your computer and Google Drive',
    long_description = long_description,
    author = 'Tormod Landet',
    url = 'https://bitbucket.org/trlandet/gdrive_sync',
    classifiers = ['Development Status :: 4 - Beta',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: BSD License',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'License :: OSI Approved :: Python Software Foundation License',
                   'Operating System :: OS Independent',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: System :: Archiving :: Mirroring',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Environment :: Console'],
    install_requires = ['google-api-python-client', 'python-dateutil', 'tzlocal'],
    scripts = ['scripts/gdrive_sync']
)

