from distutils.core import setup

setup(
    name='django_teamcity_test_runner',
    version='0.1.0',
    author='Stanislau Charniakou',
    author_email='stas.cherniakov@gmail.com',
    packages=['teamcity_runner'],
    url='http://pypi.python.org/pypi/django_teamcity_test_runner/',
    license='LICENSE.txt',
    description='Provides test-runner class to django projects to be run on TeamCity',
    long_description=open('README.rst').read(),
    install_requires=[
        "Django >= 1.4.1",
        "teamcity-messages == 1.6",
        ],
)