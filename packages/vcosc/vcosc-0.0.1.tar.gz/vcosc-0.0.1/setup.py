from setuptools import setup

setup(
        name='vcosc',
        version='0.0.1',
        description='A set of tools to provide message passing between a custom DAC and OSC',
        url='http://hecanjog.com',
        author='He Can Jog',
        author_email='erik@hecanjog.com',
        license='Public Domain',
        packages=['vcosc'],
        install_requires=[
            'pyOSC',
            'docopt',
        ],
        test_suite='nose.collector',
        tests_require=['nose'],
        scripts=['bin/vc'],
        zip_safe=False
    )
