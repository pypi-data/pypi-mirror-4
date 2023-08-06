from setuptools import setup, find_packages
import os

try:
    from setuptest import test
except ImportError:
    from setuptools.command.test import test

version = '0.0.4'

def read(fname):
    # read the contents of a text file
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-yacaptcha",
    version = version,
    url = 'http://github.com/Atomic-Creative/django-yacaptcha',
    license = 'BSD',
    platforms=['OS Independent'],
    description = "Simple captcha with Yandex API.",
    long_description = read('README.md'),
    author = 'avigmati',
    author_email = 'avigmati@gmail.com',
    packages=find_packages(),
    install_requires = (
        'Django>=1.3',
	'cleanweb',
    ),
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
