from distutils.core import setup


setup(name='deltacloud',
      version='0.9.0',
      description='Python client library for Deltacloud API',
      author='Michal Fojtik',
      author_email='mfojtik@redhat.com',
      maintainer='Tomas Sedovic',
      maintainer_email='tomas@sedovic.cz',
      url='http://deltacloud.apache.org/',
      py_modules=['deltacloud'],
      requires=['requests (>=1.0)'],
      classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      long_description = open('README.rst').read(),
      )
