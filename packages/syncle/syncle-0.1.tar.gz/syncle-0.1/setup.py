from setuptools import setup

setup(
  name = 'syncle',
  description = 'Single file synchronization tool',
  author = 'Roman Dolgushin',
  author_email = 'rd@roman-dolgushin.ru',
  url = 'https://github.com/rdolgushin/syncle',
  license = 'MIT',
  version = '0.1',
  packages = ['syncle'],
  install_requires = ['PyYAML'],
  entry_points = {
    'console_scripts': ['syncle = syncle.syncle:main']
  },
  classifiers = [
    'Topic :: Utilities',
    'Topic :: Communications :: File Sharing',
    'Environment :: Console',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX'
  ],
)
