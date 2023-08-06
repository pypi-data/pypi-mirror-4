from setuptools import setup

version = '0.6.4'

setup(
    name="uaverify",
    version=version,
    description='Urban Airship Build Verification',
    long_description=open('README.rst').read(),
    author='Urban Airship',
    author_email='support@urbanairship.com',
    url='https://github.com/urbanairship/powercar',
    packages=['uaverify'],
    package_data={
        '': ['LICENSE', 'README.rst'],
        'uaverify': ['*.cfg'],
    },
    license='APLv2',
    tests_require=['nose'],
    entry_points={
        'console_scripts': ['uaverify=uaverify.uainspector:main'],
    },
)

