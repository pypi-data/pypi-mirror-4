from setuptools import setup, find_packages
import os

version = '0.2.0'

setup(name='z3c.taskqueue',
      version=version,
      description="Task queue service",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Godefroid Chapelle and the Zope community',
      author_email='zope-dev@zope.org',
      url='',
      license='ZPL 2.1',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['z3c'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'zope.interface',
          'zope.component',
          'zope.schema',
          'zope.configuration',
          'zope.container',
          'zc.queue',
          'zope.app.publication',
      ],
      extras_require=dict(test=['zope.app.testing',
        ]),
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
