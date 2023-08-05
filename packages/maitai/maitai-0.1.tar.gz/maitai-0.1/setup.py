from setuptools import setup


setup(name="maitai",
      version='0.1',
      description='Handy WSGI Middleware Utilities',
      long_description='',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
      ],
      keywords='wsgi middleware cookies errors',
      url='http://github.com/storborg/maitai',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=[
          'webob',
          # These are for tests.
          'coverage',
          'nose>=1.1',
          'nose-cover3',
          'webtest',
      ],
      license='MIT',
      packages=['maitai'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
