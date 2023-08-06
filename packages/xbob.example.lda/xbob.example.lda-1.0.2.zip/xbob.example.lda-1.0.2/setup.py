from setuptools import setup, find_packages

setup(

    name='xbob.example.lda',
    version='1.0.2',
    description='(Fisher) Iris Flower LDA example',
    url='http://pypi.python.org/pypi/xbob.example.lda',
    license='GPLv3',
    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',
    long_description=open('README.rst').read(),

    packages=find_packages(),
    include_package_data=True,

    install_requires=[
      'setuptools',
      'bob >= 1.1.0',
    ],

    entry_points={
      'console_scripts': [
        'iris.py = xbob.example.lda.iris:main',
        ],
      },

    namespace_packages = [
      'xbob',
      'xbob.example',
    ],

    classifiers = [
      'Development Status :: 5 - Production/Stable',
      'Intended Audience :: Education',
      'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
      'Natural Language :: English',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
)
