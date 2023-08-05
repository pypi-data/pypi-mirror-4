from setuptools import setup


f = open('requirements.txt')
required_packages = f.readlines()
f.close()
test_requirements = required_packages[:]
test_requirements.append('mock')

f = open('README.rst')
readme = f.read()
f.close()

setup(
    name='Flask-Heroku-Runner',
    version='2',
    license='BSD',
    author='Dave Shawley',
    author_email='daveshawley@gmail.com',
    url='http://bitbucket.org/daveshawley/flask-heroku-runner/',
    description='Minimalist Heroku bootstrap for Flask',
    long_description=readme,
    py_modules=['flask_heroku_runner'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=required_packages,
    tests_require=test_requirements,
    test_suite='tests',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)

