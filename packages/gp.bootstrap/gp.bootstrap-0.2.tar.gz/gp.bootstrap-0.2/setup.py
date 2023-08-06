from setuptools import setup, find_packages
import os

version = '0.2'


def read(*names):
    values = dict()
    for name in names:
        filename = name+'.txt'
        if os.path.isfile(filename):
            value = open(name+'.txt').read()
        else:
            value = ''
        values[name] = value
    return values


long_description = """
%(README)s

News
====

%(CHANGES)s

""" % read('README', 'CHANGES')

setup(name='gp.bootstrap',
      version=version,
      description="Small script to deal with zc.buildout bootstrapping",
      long_description=long_description,
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
          'Operating System :: POSIX',
      ],
      keywords='',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'docs', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
          'setuptools',
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      bootstrap = gpbootstrap:main
      """,
      )
