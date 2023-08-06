Urban Airship Power Car
=======================

Command line tool for inspecting iOS builds using built in development tools and
the Urban Airship API.

The tool uses the codesign tool in OS X to parse entitlements from a built app.
Those entitlements, combined with the build settings and values from the AirshipConfig.plist
embedded in the app bundle are used in an API call which returns UA server side app
settings. These value are compared to produce a simple pass/fail command line output
indicating whether or not the settings are valid.

Python Setup
------------

Future versions will be available with pip install.  This tool was built for the default OS X (10.8.2) Python 2.7.2 build. It has not been extensively tested with other versions of Python. You can change the OS X system python version with the python versioner. Checkout the man page for Python for more details.

You can install with easy_install or pip install, if you want the release tool. If you are using the system python, this will require
sudo. I would recommend using virtualenv for python work on OS X. Release install looks like:

easy_install uaverify or pip install uaverify

If you want to work on the tool, this is a useful install method. Run it from the root of the project repo::

    python setup.py develop

If you want to take the tool out for a spin directly from the repository, this command will install
it in your local bin::

    pip install -e "git+git@github.com:urbanairship/powercar.git#egg=uaverify"


Usage
-----

Standard usage::

    uaverify /path/to/app

Diagnostic usage::

    uaverify /path/to/app -d

The `-d` command line flag will product a diagnostic file by logging to stdout
and a file at the same time with the additional step of appending the raw
entitlements, api response, and AirshipConfig.plist data to the end of the
file. You can append this file to support correspondence or bug reports.

`xcodebuild` can be used to parse out the location of the build. The following
will print out the build when run in the root project directory (where
MyProject.xcodeproj lives).  There are several combinations of build settings
that will accomplish this, here is an example of one way::

    xcodebuild -project MyProject.xcodeproj -showBuildSettings | grep BUILT_PRODUCTS_DIR

followed by::

    xcodebuild -project MyProject.xcodeproj -showBuildSettings | grep FULL_PRODUCT_NAME

And then combine the output. Depending on your configuration, there may be a
more efficient way.
