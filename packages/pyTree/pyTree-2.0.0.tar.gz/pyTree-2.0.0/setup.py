'''
Created on Sep 2, 2012

@author: yoyzhou
'''

from distutils.core import setup

setup(
      name='pyTree',
      version='2.0.0',
      description='A list-derived TREE data structure in Python 3',
      author='Yoyo Zhou',
      author_email='iamyoyozhou@gmail.com',
      url='https://github.com/yoyzhou/pyTree',
      packages=['pyTree'],
      package_dir={'pyTree': 'src/pyTree'},
      classifiers=[
          'Development Status :: 4 - Beta ',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License    ',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Topic :: Utilities',
           'Topic :: Software Development'
          ]
       )
