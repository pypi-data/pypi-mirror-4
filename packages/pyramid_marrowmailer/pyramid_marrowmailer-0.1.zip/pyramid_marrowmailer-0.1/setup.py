# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name='pyramid_marrowmailer',
      version='0.1',
      description='Pyramid integration package for marrow.mailer,'
        ' formerly known as TurboMail',
      long_description=read('README.rst') +
                       read('HISTORY.rst') +
                       read('LICENSE'),
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
      ],
      keywords='web wsgi pylons pyramid',
      author='',
      author_email='domen@dev.si',
      url='https://github.com/iElectric/pyramid_marrowmailer',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'pyramid',
          'pyramid_tm',
          'marrow.mailer',
          'setuptools',
          'transaction',
      ],
      extras_require={
          'test': [
              'nose',
              'coverage',
              'setuptools-flakes',
              'pep8',
          ],
      },
      entry_points="""
      """,
      include_package_data=True,
      zip_safe=False,
      )
