from distutils.core import setup
from setuptools import find_packages


setup(
    name='django-proxy-users',
    version='0.0.8',
    author='Jesus Rodriguez',
    author_email='jesus.rodriguez.ravelo@gmail.com',
    packages=find_packages(),
    url='https://github.com/jturo/django-proxy-users.git',
    license='LICENSE.txt',
    include_package_data=True,
    description='Authentication extension to enable proxy users in django.',
    long_description=open('README.txt').read(),
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
    ],
    install_requires=[
        "Django >= 1.4.1",
    ],
)
