from setuptools import setup, find_packages
import sys, os

version = '0.4.1'

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.rst')).read()
except IOError:
    README = ''

setup(name='tgext.scss',
      version=version,
      description="SCSS for TurboGears2, fast middleware to use SCSS for all your CSS",
      long_description=README,
      classifiers=[
        "Environment :: Web Environment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: TurboGears"
        ],
      keywords='turbogears2.extension SCSS WSGI',
      author='Alessandro Molina',
      author_email='alessandro.molina@axant.it',
      url='http://bitbucket.org/_amol_/tgext.scss',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      namespace_packages=['tgext'],
      include_package_data=True,
      package_data = {'':['*.html', '*.js', '*.css', '*.png', '*.gif']},
      zip_safe=False,
      install_requires=[
        "TurboGears2 >= 2.0b7",
        "libsass >= 0.2.4"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
