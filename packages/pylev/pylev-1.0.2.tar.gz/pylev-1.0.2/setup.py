import os
from distutils.core import setup

setup(
    name='pylev',
    version='1.0.2',
    description="A pure Python Levenschtein implementation that's not freaking GPL'd.",
    author='Daniel Lindsley',
    author_email='daniel@toastdriven.com',
    long_description=open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'r').read(),
    py_modules=['pylev'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    url='http://github.com/toastdriven/pylev'
)
