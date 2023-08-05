from setuptools import setup

setup(name='picomongo',
      version='0.6',
      description='Ultimate MongoDB Object Document Mapper',
      author='Dailymotion IT Team',
      author_email='contact@dmcloud.net',
      packages=['picomongo'],
      install_requires=['pymongo'],
      classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Topic :: Database',
      ]
)
