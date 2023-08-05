===========
Django TeamCity Test Runner
===========

A simple package that provides test runner class for building your Django projects on TeamCity server

    *Uses teamcity-messages==1.6

Usage:
_____
in your settings.py insert:
::
    TEST_RUNNER = 'teamcity_runner.TeamCityTestRunner'

Required:
________

    * Django >= 1.4.1
    * teamcity-messages == 1.6