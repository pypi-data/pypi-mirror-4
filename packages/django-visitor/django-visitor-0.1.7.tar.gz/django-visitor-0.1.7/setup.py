from distutils.core import setup

setup(
    name='django-visitor',
    version='0.1.7',
    description='Track visitors across your site using a cookie',
    maintainer='Ken Cochrane',
    maintainer_email='KenCochrane@gmail.com',
    url='https://bitbucket.org/kencochrane/django-visitor/',
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    packages=['visitor',],
    long_description=open('README').read(),
)

