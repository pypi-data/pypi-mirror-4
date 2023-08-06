# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='sersic',
    version='1.0.0',
    license='MIT (X11) License',
    author='Greg Novak',
    author_email='greg.novak@gmail.com',
    packages=['sersic', 'sersic'],
    # http://launchpad.net/sersic
    url='http://pypi.python.org/pypi/sersic/',
    description='Exact deprojection of Sérsic surface brightness profiles.',
    long_description=open('README').read(),
)
