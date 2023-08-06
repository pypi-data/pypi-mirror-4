import os
from setuptools import setup, find_packages


def read_file(filename):
    """Read a file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''


setup(
    name='epfl-sphinx-theme',
    version=__import__('epfl_theme').__version__,
    author='EPFL/SI/DIT/KIS',
    author_email='webmaster@epfl.ch',
    keywords = 'sphinx extension theme epfl',
    
    packages=find_packages(),
    package_data={'epfl_theme': ["theme/epfl/*.*", "theme/epfl/static/*.*"] },
    include_package_data=True,
    zip_safe=False,

    url='http://kis-doc.epfl.ch/sphinx/',
    license = "GNU General Public License (GPL)",
    description = "A Sphinx theme for EPFL (web2010)",
    long_description=read_file('README.rst'),

    install_requires=('sphinx>=1.1', ),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        # XXX: there should be a "Framework :: Sphinx :: Extension" classifier :)
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ] 
    
)