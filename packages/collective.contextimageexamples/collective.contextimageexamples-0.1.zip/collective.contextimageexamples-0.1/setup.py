from setuptools import setup, find_packages
import os

version = "0.1"
shortdesc = ('Some examples for context.contextimage')
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'HISTORY.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()

setup(name='collective.contextimageexamples',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Software Development',
            "Framework :: Plone",
            "Framework :: Plone :: 4.1",
            "Framework :: Plone :: 4.2",
      ],
      keywords='web zope plone theme context.contextimage',
      author='Espen Moe-Nilssen',
      author_email='espen@medialog.no',
      url="http://pypi.python.org/pypi/collective.contextimageexamples",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.contextimage',
      ],
      entry_points="""
      # -*- Entry points: -*-
      
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
