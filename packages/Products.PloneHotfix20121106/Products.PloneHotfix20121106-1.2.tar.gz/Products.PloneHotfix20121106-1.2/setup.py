from setuptools import setup, find_packages

import os

long_description = open(os.path.join('Products', 'PloneHotfix20121106', "README.txt")).read() + "\n" + \
                   open(os.path.join("docs", "HISTORY.txt")).read()

version = '1.2'

setup(name='Products.PloneHotfix20121106',
      version=version,
      description="Various Plone hotfixes, 2012-11-06",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='plone security hotfix patch',
      author='Plone Security Team',
      author_email='security@plone.org',
      url='http://github.com/plone',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
      ],
      extras_require={
          'test': [
              'Pillow',
              'Plone',
              'Products.PloneTestCase'
              ],
          'test-plone2': [
              'Products.PloneTestCase',
              ],
          'test-plone31': [
              'archetypes.kss',
              'borg.localrole',
              'kss.core',
              'kss.demo',
              'plone.app.content',
              'plone.app.contentmenu',
              'plone.app.contentrules',
              'plone.app.controlpanel',
              'plone.app.customerize',
              'plone.app.form',
              'plone.app.i18n',
              'plone.app.iterate',
              'plone.app.kss',
              'plone.app.layout',
              'plone.app.linkintegrity',
              'plone.app.openid',
              'plone.app.portlets',
              'plone.app.redirector',
              'plone.app.viewletmanager',
              'plone.app.vocabularies',
              'plone.app.workflow',
              'plone.browserlayer',
              'plone.contentrules',
              'plone.fieldsets',
              'plone.i18n',
              'plone.intelligenttext',
              'plone.keyring',
              'plone.locking',
              'plone.memoize',
              'plone.openid',
              'plone.portlets',
              'plone.protect',
              'plone.session',
              'plone.theme',
              'plone.portlet.collection',
              'plone.portlet.static',
              'wicked',
              'five.customerize',
              'five.localsitemanager',

              'Pillow',
              'Products.PloneTestCase'
              ],
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """
      )
