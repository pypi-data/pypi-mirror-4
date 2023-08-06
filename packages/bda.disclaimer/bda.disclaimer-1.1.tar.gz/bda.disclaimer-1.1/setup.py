from setuptools import setup, find_packages
import sys, os

version = '1.1'
shortdesc ="Cookie based access restriction for Plone sites."
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


setup(name='bda.disclaimer',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'Environment :: Web Environment',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      keywords='plone cookie protection disclaimer',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url='http://pypi.python.org/pypi/bda.disclaimer',
      license='GPL',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['bda'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools', 
          # -*- Extra requirements: -*
      ],
      extras_require={
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """)
