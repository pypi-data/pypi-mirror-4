from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
      name='etree-trunc',
      version='0.1',
      author = 'Szymon Pyżalski',
      author_email = 'zefciu <szymon@pythonista.net>',
      description = 'Truncates an etree',
      long_description = long_description,
      keywords = 'html truncate',
      packages=find_packages(),
      classifiers = [
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
      ]
)
