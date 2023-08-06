import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (read('README.rst') + '\n' + read('CHANGES.txt') + '\n')


name = 'githubbuildout'


setup(
    name=name,
    version="0.2",
    author="Kevin Williams",
    author_email="kevin@weblivion.com",
    description="Buildout extension to enable downloads from private GitHub "
                "repositories into buildout find-links and download recipes",
    long_description=long_description,
    license="ZPL 2.1",
    keywords="buildout github private repository download",
    url='https://github.com/isolationism/githubbuildout',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    install_requires=['setuptools', 'zc.buildout'],
    entry_points={'zc.buildout.extension':
                  ['default = %s.githubbuildout:install' % name]},
    zip_safe=False,
    classifiers=[
       'Development Status :: 4 - Beta',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Framework :: Buildout :: Extension',
       'Topic :: Software Development :: Build Tools',
    ],
)
