#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>
# Sun 20 Jan 18:22:00 2013 CEST

from setuptools import setup, find_packages

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='xbob.db.wine',
    version='1.0.2',
    description='Wine Database for bob',
    url='http://github.com/bioidiap/xbob.db.wine',
    license='GPLv3',
    author='Laurent El Shafey',
    author_email='laurent.el-shafey@idiap.ch',

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    # This line defines which packages should be installed when you "install"
    # this package. All packages that are mentioned here, but are not installed
    # on the current system will be installed locally and only visible to the
    # scripts of this package. Don't worry - You won't need adminstrative
    # privileges when using buildout.
    install_requires=[
      'setuptools',
      'bob', # base signal proc./machine learning library
    ],

    # Your project should be called something like 'xbob.<foo>' or
    # 'xbob.<foo>.<bar>'. To implement this correctly and still get all your
    # packages to be imported w/o problems, you need to implement namespaces
    # on the various levels of the package and declare them here. See more
    # about this here:
    # http://peak.telecommunity.com/DevCenter/setuptools#namespace-packages
    #
    # Our database packages are good examples of namespace implementations
    # using several layers. You can check them out here:
    # https://github.com/idiap/bob/wiki/Satellite-Packages
    namespace_packages = [
      'xbob',
      'xbob.db',
    ],

    # This entry defines which scripts you will have inside the 'bin' directory
    # once you install the package (or run 'bin/buildout'). The order of each
    # entry under 'console_scripts' is like this:
    #   script-name-at-bin-directory = module.at.your.library:function
    #
    # The module.at.your.library is the python file within your library, using
    # the python syntax for directories (i.e., a '.' instead of '/' or '\').
    # This syntax also omits the '.py' extension of the filename. So, a file
    # installed under 'example/foo.py' that contains a function which
    # implements the 'main()' function of particular script you want to have
    # should be referred as 'example.foo:main'.
    #
    # In this simple example we will create a single program that will print
    # the version of bob.
    entry_points={

      # bob database declaration
      'bob.db': [
        'wine = xbob.db.wine.driver:Interface',
        ],

      # bob unittest declaration
      'bob.test': [
         'wine = xbob.db.wine.test:WineDatabaseTests',
         ],
      },

    # Classifiers are important if you plan to distribute this package through
    # PyPI. You can find the complete list of classifiers that are valid and
    # useful here (http://pypi.python.org/pypi?%3Aaction=list_classifiers).
    classifiers = [
      'Development Status :: 4 - Beta',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      'Topic :: Database :: Front-Ends',
      ],
)
