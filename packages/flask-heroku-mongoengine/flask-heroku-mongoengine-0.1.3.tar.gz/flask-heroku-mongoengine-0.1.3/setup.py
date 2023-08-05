"""
Flask-Heroku
------------

This is a super simple Flask extension that provides some app configuration
defaults based on the Heroku-esque environment variables.
"""

from distutils.core import setup


setup(
    name='flask-heroku-mongoengine',
    version='0.1.3',
    url='https://github.com/bjackson/flask-heroku',
    license='BSD',
    author='Brett Jackson',
    author_email='brettbj.jackson@gmail.com',
    description='Heroku environment variable configurations for Flask. (Modfified from Kenneth Reitz)',
    long_description=__doc__,
    py_modules=['flask_heroku_mongoengine'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=['Flask'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
