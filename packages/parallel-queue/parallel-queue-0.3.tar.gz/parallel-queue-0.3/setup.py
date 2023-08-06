from setuptools import setup
from parallel_queue import __version__


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='parallel-queue',
      version=__version__,
      description='A multi-process task queue that maintains FIFO order.',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Operating System :: OS Independent',
          'Topic :: Utilities',
      ],
      keywords='',
      packages=('parallel_queue',),
      include_package_data=True,
      zip_safe=False,
      install_requires=(),
      author='Tikitu de Jager',
      author_email='tikitu@logophile.org')
