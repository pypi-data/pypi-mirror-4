from os import path
import codecs
from setuptools import setup, find_packages

read = lambda filepath: codecs.open(filepath, 'r', 'utf-8').read()

tests_require = [
    'Django>=1.2',
    'nose==1.2.1',
    'nose-setenv',
    'mock>=0.7.2',
    'httpretty',
    'sure',
]

setup(
    name='django-twitter-tag',
    version='1.0',
    author='Ilya Baryshev',
    author_email='baryshev@gmail.com',
    packages=find_packages(exclude="tests"),
    url='https://github.com/coagulant/django-twitter-tag',
    license='MIT',
    description="A django template tag to display user's recent tweets.",
    long_description=read(path.join(path.dirname(__file__), 'README.rst')),
    dependency_links=[
        'https://github.com/coagulant/twitter-text-python/tarball/master#egg=twitter-text-python-1.0',
    ],
    install_requires=[
        "django-classy-tags==0.4",
        "twitter==1.9.1",
        "django-appconf==0.6",
        "twitter-text-python==1.0"
    ],
    tests_require=tests_require,
    test_suite = "nose.collector",
    extras_require={'test': tests_require},
    classifiers = [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
    ],
)