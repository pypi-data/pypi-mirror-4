from setuptools import setup
import sys


# no with statement for python 2.5
def long_description():
    f = open('README.rst')
    rst = f.read()
    f.close()
    return rst


packages = ['redis_sessions']


install_requires = [
    'redis>=2.4.10',
    'django>=1.4'
]

if not "__pypy__" in sys.builtin_module_names:
    major, minor = sys.version_info[:2]
    if (major, minor) != (2, 5):
        install_requires.append('hiredis>=0.1.1')


setup(
    name='django-redis-sessions-fork',
    version='0.5.2',
    description="Redis Session Backend For Django",
    long_description=long_description(),
    keywords='django, sessions, redis',
    author='Martin Rusev',
    author_email='hellysmile@gmail.com',
    url='https://github.com/hellysmile/django-redis-sessions-fork',
    license='BSD',
    packages=packages,
    zip_safe=False,
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Django",
        "Environment :: Web Environment",
    ],
)
