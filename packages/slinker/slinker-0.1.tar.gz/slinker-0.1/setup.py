from setuptools import setup

readme = open('README.rst').read()
import slinker
version = slinker.__version__

setup(name="slinker",
      version=version,
      packages=['slinker'],
      author='Young King',
      author_email='jek@discorporate.us',
      description='A signal one to one event',
      keywords='signal event emit rpc',
      long_description=readme,
      license='MIT License',
      url='http://www.flyzen.com',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities',
      ],
      )
