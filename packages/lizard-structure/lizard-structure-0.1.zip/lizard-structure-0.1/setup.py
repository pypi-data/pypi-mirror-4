from setuptools import setup

version = '0.1'

long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CREDITS.rst').read(),
    open('CHANGES.rst').read(),
    ])

install_requires = [
    'Django',
    'django-nose',
    'djangorestframework >= 2.0',
    'south',
    ],

setup(name='lizard-structure',
      version=version,
      description=("Structure of Lizard, defined and documented " +
                   "in a REST interface"),
      long_description=long_description,
      # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=['Programming Language :: Python',
                   'Framework :: Django',
                   ],
      keywords=[],
      author='Reinout van Rees',
      author_email='reinout.vanrees@nelen-schuurmans.nl',
      url='https://github.com/lizardsystem/lizard-structure',
      license='GPL',
      packages=['lizard_structure'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points={
          'console_scripts': [
          ]},
      )
