from setuptools import setup, find_packages

setup(
    name='django-recaptcha-mozilla',
    version='0.0.1',
    description='Mozilla fork of django recaptcha form field/widget app.',
    long_description = open('README.rst', 'r').read(),
    author='Praekelt Foundation',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/mozilla/django-recaptcha',
    packages = find_packages(),
    install_requires = [
        'recaptcha-client'
    ],
    include_package_data=True,
    classifiers = [
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
