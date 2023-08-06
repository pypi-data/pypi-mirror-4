from setuptools import setup, find_packages

setup(
    name='Flask-DebugToolbar-Mongo',
    version="0.1",
    description='MongoDB panel for the Flask Debug Toolbar',
    long_description=open('README.rst').read(),
    author='Bruno Carlin',
    author_email='bruno@bcarlin.net',
    url='https://github.com/bcarlin/flask-debugtoolbar-mongo',
    license='MIT',
    packages=find_packages(exclude=('example', )),
    include_package_data=True,
    zip_safe=False,
    setup_requires=[
        'Flask>=0.8',
        'pymongo',
        'Flask-DebugToolbar',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
