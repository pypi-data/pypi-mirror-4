from setuptools import setup

README_file = open('README.rst')
README = README_file.read()
README_file.close()

setup(name='clifig',
      version='0.1',
      description='A simple prompt to modify config files.',
      long_description=README,
      keywords='ConfigParser command-line cli config configuration conf',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Development Status :: 3 - Alpha',
                   'Operating System :: OS Independent',
                   'Topic :: Utilities'],
      url='https://github.com/andrewguenther/clifig',
      author='Andrew Guenther',
      author_email='guenther.andrew.j@gmail.com',
      license='MIT',
      packages=['clifig'],
      scripts=['bin/clifig']
     )
