from setuptools import setup, find_packages

version = '0.1'

setup(name='ramp',
      version=version,
      description="Rapid machine learning prototyping",
      long_description=open("README.md").read(),
      classifiers=[
          'License :: OSI Approved :: BSD License'
      ],
      keywords='machine learning data analysis statistics mining',
      author='Ken Van Haren',
      author_email='kvh@science.io',
      url='http://github.com/kvh/ramp',
      license='BSD',
      packages=find_packages(exclude=["*.tests"]),
      zip_safe=False,
      install_requires=[
          'numpy',
          'pandas',
          'scikit-learn',
      ]
      )

