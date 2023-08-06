Urban Airship Verification
==========================

Command line tools for verifying builds with Urban Airship. Two command line tools
are installed, one for use with iOS builds, one for use with Android builds.

Setup for Use
-------------

The script is written against the default install of Python 2.7.2 installed on OS X 10.8.3.
It's been designed to have no third party dependencies. Running on a previous version of
Python has not been thoroughly tested, and my have issues. You can set the default
Python version with the following command, see *man python* for more details
::
    defaults write com.apple.versioner.python Version 2.7

You can install the tool multiple ways. If you aren't using a virtualenv, you'll
need to sudo to install the tool::

    pip install uaverify (if pip is available) or easy_install uaverify


Setup for Development
---------------------

If you want to work on the tools themselves, this is a useful install method.
Run it from the root of the project repo::

    python setup.py develop

If you want to take the tool out for a spin directly from the repository, this command will install
it in your local bin::

    pip install -e "git+git@github.com:urbanairship/uaverify.git#egg=uaverify"


Usage
-----

**Breaking changes from previous release**
uaverify has now changed to uav-ios with the addition of the uav-android tool. Now both tools are
installed at the same time. 

This::

    uaverify /path/to/app

is now::

    uav-ios /path/to/app <--> uav-android /path/to/project/dir


**Standard usage for iOS**::

    uav-ios /path/to/app

The path to the build output (the AppName.app) bundle is dependent on the Xcode build configuration.
Please see the Xcode documentation for more details:

http://developer.apple.com/library/mac/#documentation/DeveloperTools/Reference/XcodeBuildSettingRef/0-Introduction/introduction.html

You can use xcodebuild to locate the build output path, specifically the CODESIGNING_FOLDER_PATH parameter. This path changes
according to your build settings, so make sure and use the proper configuration. See the xcodbuild manpage for more information

**Standard usage for Android**::

    uav-android /path/to/project/directory

**For projects with more than one AndroidManifest, you'll need to pass the path to the manifest you want to use.**::

    uav-android /path/to/project/directory -m /path/to/manifest

**Diagnostic usage for either tool**::

    uav-ios /path/to/app -d or uav-android /path/to/project/dir/ -d

The `-d` command line flag will product a diagnostic file by logging to stdout
and a file at the same time with the additional step of appending the raw
entitlements, API response, and AirshipConfig.plist data to the end of the
file. You can append this file to support correspondence or bug reports.
