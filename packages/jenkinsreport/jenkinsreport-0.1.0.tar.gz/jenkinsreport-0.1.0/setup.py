from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='jenkinsreport',
      version='0.1.0',
      description='Tools for reporting Jenkins test results information',
      url='http://github.com/sachu/jenkinsreport',
      author='Stephen Chu',
      author_email='chu.stephen@gmail.com',
      license='MIT',
      packages=['jenkinsreport'],
      install_requires=[
        'jenkinsapi',
        'pandas',
      ],
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points = {
         'console_scripts': ['fetch_test_results=jenkinsreport.command_line:fetch_test_results'],
      },
     )
