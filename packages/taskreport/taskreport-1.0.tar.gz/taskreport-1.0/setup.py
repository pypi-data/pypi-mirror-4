#!/usr/bin/python

from distutils.core import setup

setup(name='taskreport',
      version='1.0',
      description='Automatic reporting tool for Taskwarrior',
      long_description=open('README.txt').read(),
      author='Alicia BEL & Thibaut HOREL',
      author_email='task.report.python@gmail.com',
      license='GNU GPLv3',
      classifiers=['Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Office/Business :: Scheduling',
                   'Topic :: Utilities'
                   ],
      scripts=['taskreport'],
      data_files=[('share/taskreport',['data/email_template.html', 'data/config.sample',
                                        'LICENSE.txt'])]
      )

