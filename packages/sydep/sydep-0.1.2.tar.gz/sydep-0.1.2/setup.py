from distutils.core import setup

setup(
    name='sydep',
    version='0.1.2',
    author='Juda Kaleta',
    author_email='juda.kaleta@gmail.com',
    url='https://github.com/yetty/sydep',
    license=open('LICENSE.txt').read(),
    description='tool for easy deployment over rsync',
    long_description=open('README.txt').read(),
    packages=['sydep', 'sydep.test'],
    scripts=['bin/sydep'],
    requires=['docopt (>= 0.6.1)', ],
    package_data={'sydep': ['sydep.cfg.sample']},

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
