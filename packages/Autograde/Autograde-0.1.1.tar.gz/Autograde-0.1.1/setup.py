from distutils.core import setup

setup(
    name='Autograde',
    version='0.1.1',
    author='Henry Bradlow',
    author_email='henrybrad@gmail.com',
    packages=['autograde'],
    scripts=[],
    url='http://pypi.python.org/pypi/Autograde/',
    license='LICENSE.txt',
    description='A django autograder.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.4.1",
        "django-extensions >= 0.9",
        "django-tastypie >= 0.9.11",
        "requests >= 0.14.0",
    ],
)
