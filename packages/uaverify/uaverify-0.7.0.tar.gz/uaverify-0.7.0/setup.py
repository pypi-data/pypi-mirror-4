#    Copyright 2012 Urban Airship
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from setuptools import setup

version = '0.7.0'

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
    tests_require=['nose', 'mock'],
    entry_points={
        'console_scripts': ['uav-ios=uaverify.uainspector:iosmain',
                            'uav-android=uaverify.uainspector:androidmain'],
    },
)

