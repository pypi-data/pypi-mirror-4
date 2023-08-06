from setuptools import setup, find_packages
import os.path

version = '1.3'

setup(name='Products.i18ntestcase',
      version=version,
      description="Products.i18ntestcase is build on top of the ZopeTestCase "
                  "package. It has been developed to simplify testing of "
                  "gettext i18n files for Zope products.",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
      ],
      keywords='Plone i18n gettext testcase',
      author='Hanno Schlichting',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://github.com/plone/Products.i18ntestcase',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'setuptools',
      ],
)
