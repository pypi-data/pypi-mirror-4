from setuptools import setup, find_packages
import os

version = '0.4'

setup(name='pcommerce.payment.paypal',
      version=version,
      description="A paypal payment method for PCommerce",
      long_description = (
            open('README.txt').read()
            + '\n\n' +
            'History\n'
            '=======\n'
            + '\n\n' +
            open('CHANGES.txt').read()
            + '\n'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Steffen Lindner',
      author_email='gomez@flexiabel.de',
      url='https://github.com/Gomez/pcommerce.payment.paypal',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['pcommerce', 'pcommerce.payment'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pcommerce.core>0.4',
          'paypal==1.2.0'
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
