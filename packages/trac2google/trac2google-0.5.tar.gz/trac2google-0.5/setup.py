from setuptools import setup, find_packages
import sys, os

version = '0.5'

setup(name='trac2google',
      version=version,
      description="A simple script that will read a Trac timeline RSS feed, look for tickets and put them on a timesheet calendar in Google",
      long_description="""\
Running it the first time will create a new file in your home, called 
.gcalendar. You need to fill in your google account details, your trac 
id and the name of the calendar that contains your timesheet.

IMPORTANT: this script only processes one month, it will not 
record timesheet entries in other months, so it is best if you run this 
in cron, daily, at some convenient hour when you've finished your work.

You can call it with an argument from the command, line, giving
it the number of the month that you want it to process.
""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author="Tiberiu Ichim",
      author_email='tibi@pixelblaster.ro',
      url='http://bitbucket.org/tiberiuichim/trac2google',
      license='GPL',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          'gdata',
          'lxml',
          'BeautifulSoup',
          #'pytz',
      ],
      entry_points={
          'console_scripts':[
                "trac2google = trac2google.trac:main",
                "redmine2google = trac2google.redmine:main"
              ]
          }
      )
