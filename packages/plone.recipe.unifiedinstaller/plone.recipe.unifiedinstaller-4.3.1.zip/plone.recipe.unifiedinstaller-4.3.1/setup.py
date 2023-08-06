import os
from setuptools import setup, find_packages

name = "plone.recipe.unifiedinstaller"
version = '4.3.1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


long_description = (
        read('README.rst')
        + '\n' +
        read('CHANGES.txt')
    )

setup(
    name=name,
    version=version,
    author="Steve McMahon",
    author_email="steve@dcn.org",
    description="ZC Buildout recipe for Plone Unified Installer install finalization",
    long_description=long_description,
    license="ZPL 2.1",
    keywords="zope2 buildout",
    url='https://svn.plone.org/svn/collective/buildout/plone.recipe.unifiedinstaller/trunk',
    classifiers=[
      "License :: OSI Approved :: Zope Public License",
      "Framework :: Buildout",
      "Framework :: Zope2",
      "Programming Language :: Python",
      ],
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    namespace_packages=['plone', 'plone.recipe'],
    install_requires=['setuptools', 'zc.buildout', 'zc.recipe.egg'],
    dependency_links=['http://download.zope.org/distribution/'],
    zip_safe=False,
    entry_points={'zc.buildout': ['default = %s:Recipe' % name]},
    )
