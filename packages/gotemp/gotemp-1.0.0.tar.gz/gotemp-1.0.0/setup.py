from setuptools import setup, find_packages

description = 'A library for interacting with GoTemp! temperature sensors.'
long_description = ('Allows querying of GoTemp! temperature sensors and '
                    'setting the LED color and brightness on the sensor.')

requires = []

setup(
    name='gotemp',
    version='1.0.0',
    description=description,
    long_description=long_description,
    author='Brian Cline',
    author_email='bc@brian.fm',
    url='https://github.com/briancline/gotemp-python',
    license='The BSD License',

    install_requires=requires,
    packages=find_packages(),

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Home Automation',
        'Topic :: System :: Monitoring'
    ]
)
