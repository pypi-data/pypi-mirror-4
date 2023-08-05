import os
from setuptools import setup, find_packages

version = '6.0.10'

setup(name='quintagroup.theme.schools',
      version=version,
      description="Free Diazo theme for Plone 4.2",
      long_description=open(os.path.join("quintagroup", "theme", "schools", "README.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "INSTALL.txt")).read() + "\n\n"+
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='web zope plone theme diazo quintagroup',
      author='Quintagroup',
      author_email='skins@quintagroup.com',
      url='http://skins.quintagroup.com/schools',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['quintagroup', 'quintagroup.theme',],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'plone.app.theming',
                        # -*- Extra requirements: -*-
                        ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
