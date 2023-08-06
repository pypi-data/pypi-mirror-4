from setuptools import setup, find_packages
readme = open('README.txt').read()
setup(name='eusful',
      version='0.1',
      author='Eugene Efremov',
      author_email='eaefremov@gmail.com',
      license='MIT',
      description='This is a small package of useful functions I do not want to rewrite or copy-paste.',
      long_description=readme,
      packages=find_packages())