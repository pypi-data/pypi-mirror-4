from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "kupu", "version.txt")).read()

setup(name='Products.kupu',
      version=version,
      description="",
      long_description=open(os.path.join("Products", "kupu", "doc", "README.txt")).read() + "\n" +
                       open(os.path.join("Products", "kupu", "doc", "CHANGES.txt")).read().decode('latin1').encode('ascii','replace'),
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='',
      author='Kupu Team',
      author_email='kupu-dev@codespeak.net',
      license='Kupu License',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'i18ndude',
            'Products.CMFPlone',
            'Products.ATContentTypes',
            'Products.i18ntestcase',
            'Products.PloneTestCase',
        ]
      ),
      install_requires=[
          'setuptools',
          'plone.outputfilters',
          'zope.interface',
          'zope.schema',
          'zope.i18n',
          'zope.i18nmessageid',
          'Products.Archetypes',
          'Products.GenericSetup',
          'Products.CMFCore',
          'Products.CMFPlone>=4.1a1',
          'Products.MimetypesRegistry',
          'Products.PortalTransforms',
          'zope.app.component',
          # 'Acquisition',
          # 'ZODB3',
          # 'Zope2',
      ],
      )
