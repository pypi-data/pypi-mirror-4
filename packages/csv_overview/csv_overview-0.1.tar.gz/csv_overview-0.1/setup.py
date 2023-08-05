from setuptools import setup

setup(name='csv_overview',
      version='0.1',
      description='Get the vital statistics of a CSV file',
      long_description=open('readme.md', 'rb').read(),
      url='http://github.com/sbirch/csv-overview',
      classifiers=['License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 3 - Alpha'],
      author='Sam Birch',
      author_email='sam.m.birch@gmail.com',
      license='MIT',
      packages=['csv_overview'],
      scripts=['scripts/csv-overview'],
      zip_safe=False)