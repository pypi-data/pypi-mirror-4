from distutils.core import setup

version = '0.1'
app = 'xtify'
description = 'Python module for using the Xtify webservice API'
url = 'https://github.com/h0st1le/xtify-python'
readme = open('README.md').read()

setup(
    name='%s' % app,
    version=version,
    author="Justin Penka",
    author_email="jpenka@gmail.com",
    keywords='xtify,python,webservice,api,mobile',
    url=url,
    description=description,
    long_description=readme,
    py_modules=["xtify"],
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries'
    ],
)
