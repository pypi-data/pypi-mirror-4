# -*- coding: utf-8 -*-
'''
Unity A/V Application indicator

uses amixer and modprobe for uvcvideo to enable/disable the device, also listens
to DBus for microphone status updates.
'''
from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='unity_avindicator',
      version='0.6',
      description="AV enable/disable Unity Application Indicator",
      long_description='Originally developed for a System76 Gazelle laptop.',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Programming Language :: Python :: 2.7',
          'Topic :: Multimedia :: Sound/Audio'
      ],
      keywords='gazelle system76 avcontrol webcam microphone appindicator indicator',
      url='http://www.github.com/mgmtech/sys76_unity_webmic',
      author='Matthew Miller',
      author_email='matthewgarrettmiller@gmail.com',
      license='GPLv3',
      packages=['unity_avindicator',],
      zip_safe=False,
      install_requires=[
        'execute',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      scripts=['bin/avindicator.sh'],
      entry_points={
          'console_scripts': ['webmic-status=unity_avindicator.webmic:main']}
      )

