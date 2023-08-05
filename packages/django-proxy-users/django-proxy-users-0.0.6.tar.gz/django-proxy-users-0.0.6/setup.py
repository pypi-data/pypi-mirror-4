from distutils.core import setup


setup(
    name='django-proxy-users',
    version='0.0.6',
    author='Jesus Rodriguez',
    author_email='jesus.rodriguez.ravelo@gmail.com',
    packages=['django_proxy_users'],
    url='https://github.com/jturo/django-proxy-users.git',
    license='LICENSE.txt',
    description='Authentication extension to enable proxy users in django.',
    long_description=open('README.txt').read(),
    install_requires=[
        "Django >= 1.4.1",
    ],
)
