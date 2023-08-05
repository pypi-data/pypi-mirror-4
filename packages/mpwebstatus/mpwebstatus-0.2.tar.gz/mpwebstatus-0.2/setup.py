from distutils.core import setup

setup(
    name='mpwebstatus',
    version='0.2',
    author='Chris Mutel',
    author_email='cmutel@gmail.com',
    url='https://bitbucket.org/cmutel/mpwebstatus',
    packages=['mpwebstatus'],
    package_data={'mpwebstatus': ["templates/*.html"]},
    scripts=["mpwebstatus/bin/mp_web_controller.py"],
    license='BSD 2-clause; LICENSE.txt',
    requires=["docopt", "requests", "flask"],
    long_description=open('README').read(),
)
