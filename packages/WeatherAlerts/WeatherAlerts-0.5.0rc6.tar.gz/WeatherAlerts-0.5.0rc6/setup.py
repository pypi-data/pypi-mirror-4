from setuptools import setup, find_packages

readme = open('README.rst', 'rt').read()

import sys


versionstr = '0.5.0rc6'


setup(
	name='WeatherAlerts',
    version=versionstr,
    author='Zeb Palmer',
    author_email='zeb@zebpalmer.com',
    packages=['weatheralerts'],
    package_dir={
        'weatheralerts': "weatheralerts"},
    #scripts=[ "scripts/NagiosWeatherAlerts.py",
              #"scripts/MonitorAlertsByCounty.py",
              #"scripts/NWS_Alerts.py"}
    url='http://github.com/zebpalmer/WeatherAlerts',
    license='LGPLv3',
    description='Parse the National Weather Service Emergency Alerts Feed (NWS CAP format), do useful stuff with it',
    long_description=readme,
    install_requires=['requests'],
    use_2to3=True,
    classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Environment :: Plugins',
              'Intended Audience :: Developers',
              'Intended Audience :: Education',
              'Intended Audience :: End Users/Desktop',
              'Intended Audience :: Science/Research',
              'Intended Audience :: System Administrators',
              'Intended Audience :: Telecommunications Industry',
              'License :: OSI Approved :: GNU General Public License (GPL)',
              'Natural Language :: English',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Topic :: Software Development :: Libraries :: Python Modules',
              'Topic :: Utilities'
              ],
)


