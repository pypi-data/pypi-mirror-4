from setuptools import setup, find_packages

setup(name='compass',
      version='0.1.3',
      description='Compass is a geolocation API client library offering you a flexible set of lookup strategies across a range of web services.',
      url='https://github.com/Route-Hacker/compass',
      author='Matt Rutherford',
      author_email='rutherford@clientsideweb.net',
      license='BSD',
      packages=find_packages(),
      zip_safe=False,
      test_suite='compass.tests',
      classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
      )
    )