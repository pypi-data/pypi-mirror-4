

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

""" Support methods for verifying iOS builds
"""

import sys
import string
import textwrap
import subprocess
import plistlib
import os
import re
import support

from collections import namedtuple
from xml.parsers.expat import ExpatError

# AirshipConfig.plist keys
APP_STORE_OR_AD_HOC = "APP_STORE_OR_AD_HOC_BUILD"
DEVELOPMENT_APP_KEY = "DEVELOPMENT_APP_KEY"
DEVELOPMENT_APP_SECRET = "DEVELOPMENT_APP_SECRET"
PRODUCTION_APP_SECRET = "PRODUCTION_APP_SECRET"
PRODUCTION_APP_KEY = "PRODUCTION_APP_KEY"

# API JSON Response Keys, currently the API call returns the bundle id and
# a boolean indicating whether or not th app is in production
UA_API_RESPONSE_BUNDLE_ID_KEY = "bundle_id"
UA_API_RESPONSE_PRODUCTION_KEY = "production"

# Entitlement Plist keys
ENTITLE_APP_ID_KEY = "application-identifier"
ENTITLE_APS_ENV_KEY = "aps-environment"

# Filename for deprecated plist conversion output
DEPRECATED_PLIST_PATH = "/tmp/ConvertedAirshipConfig.plist"

# APNS/UA Sever names
PRODUCTION_SERVER = "production"
DEVELOPMENT_SERVER = "development"

#setup logging
log = support.log


def clean():
    """ Cleanup any previous build cruft

    Currently only erases previous entitlement plists
    """
    entitlement_plist_path = support.get_value_from_config(
        support.ENTITLEMENTS_PLIST_PATH)

    if os.path.exists(entitlement_plist_path):
        log.info("Removing old entitlements plist file at %s",
            entitlement_plist_path)
        os.remove(entitlement_plist_path)


# API methods

APP_KEY_SECRET_INCORRECT_401 = """
The app key and secret pair are incorrect, or the app has not been setup on
Urban Airship. Please login to your account at go.urbanairship.com and review
the settings."""

APP_KEY_SECRET_INCORRECT_403 = """
The wrong value is being used for the app secret. This is the master secret,
and is used for API communication outside of the scope of a client app. It
should never be used in an app, or placed in an app bundle, as that would
be a security risk. Please review your app settings"""


def get_verification_request(ua_verification_information):
    """Get the verification request.

    The request is setup with
    basic auth headers parsed from the settings in AirshipConfig.plist
    parsed from the UAVerificationInformation passed in.

    :param ua_verification_information: VerificationInformation object
    with the data needed for this API request

    :type key: VerificationInformation
    :return: Pre authenticated http request
    :rtype: urllib2.Request
    """
    key, secret = ua_verification_information.key_secret()
    return support.get_base_verification_request(appKey=key, appSecret=secret)

def make_request_against_api(request):
    """Make a request against the UA API

    Returns a named tuple with response data as JSON and a possible error
    object which is either an HTTPError, 401,500, etc or a URLError which
    most likely occurs when there is no connection. All other errors will
    exception out. Will display the proper

    :param request: Request to make
    :type key: urllib2.Request
    :return: Named tuple in the form (response, error)
    :rtype: namedtuple
    """

    response = support.make_request_against_api(request)

    if response.error is not None:

        if response.error.code == 401:
            support.fail_log_message("Incorrect app key and secret",
                APP_KEY_SECRET_INCORRECT_401)

        if response.error.code == 403:
            support.fail_log_message("Incorrect app secret",
                APP_KEY_SECRET_INCORRECT_403)
    return response


def extract_airship_config_from_app(application_path):
    """ Attempts to read the AirshipConfig.plist out of th app bundle

    Makes the assumption the file is called AirshipConfig.plist and
    it is at the root level of the bundle

    :param application_path: Path to the .app application package
    :type key: str
    :returns: AirshipConfig.plist as a dictionary
    :rtype: dict
    """
    airship_config_plist = support.get_value_from_config(support.AIRSHIP_CONFIG_PLIST)
    path_to_plist = os.path.join(application_path, airship_config_plist)

    try:
        plist = plistlib.readPlist(path_to_plist)

    except IOError as error:
        log.error("""Error opening the plist at path %s, did you forget to at
        it to the bundle? Error %s""", path_to_plist, error.message)
        return None
    # TODO add example about fixing deprecated plist
    except ExpatError:
        support.warn_log_message("Plist parsing error, attempting to convert plist")
        plist = convert_deprecated_plist_at_path(path_to_plist)
        if plist is None:
            return None
        else:
            support.warn_log_message("Plist conversion successful, change to non deprecated "
                      "plist format to avoid this error.")

    log.debug("AirshipConfig.plist:%s", plist)
    return plist


def convert_deprecated_plist_at_path(path_to_plist):
    """Extract a deprecated plist from an app adn convert it

    :param path_to_plist: Path to the plist to convert. System call PlistBuddy
    (/usr/libexec/PlistBuddy) is made, and that converts the plist

    :type key: str
    :return: Converted plist or None on error
    :rtype: dict
    """
    plutil_command = ["/usr/bin/plutil", "-convert", "xml1", path_to_plist,
                      "-o", DEPRECATED_PLIST_PATH]
    try:
        subprocess.check_call(plutil_command)
    except subprocess.CalledProcessError as error:
        log.error("plutil conversion failed with error %s", error.message)
        return

    try:
        plist = plistlib.readPlist(DEPRECATED_PLIST_PATH)
    except ExpatError as error:
        log.error("""Cannot read converted plist, please check the format, and
                  possibly convert to the new style Error:%s""", error.message)
        return
    return plist



def execute_codesign_system_call(application_path):
    """Executes /usr/bin/codesign, and captures part of the output.

    The other part of the output is written to the /tmp dir in the form of
    a plist. If there is a CalledProcessError, an attempt to check for the
    existence of the codesign tool by calling `which codesign`, and an message
    is logged.

    :param application_path: Path to the .app application package
    :type key: str
    :returns: True if the codesign call was successful, False if not
    :rtype: bool
    """

    command = codesign_system_call_args(application_path)
    try:
        subprocess.check_call(command)

    except subprocess.CalledProcessError:
        log.error("Call process error returned from codesign system call")
        if not os.path.exists(application_path):
            log.error("""Codesign verification failed, check the path to the
             app for errors Path:%s""", application_path)
            return False
        else:
            # Check the edge case where codesign is not on the path
            try:
                subprocess.check_call(["which", "codesign"])
                return False
            except subprocess.CalledProcessError:
                log.error(textwrap.dedent(
                """Check path to codesign tool with `which codesign`
                and ensure your shell $PATH contains that path, you may
                need to install the Command Line Tools"""))
            return False

    return True


def read_entitlement_plist_from_path(path_to_plist):
    """ Reads the plist at the given path.

    This will catch an IOError exception for a bad path and return None

    :param path_to_plist: Path to the entitlement plist generated by the
    codesign call. Default output is /tmp

    :type key: str
    :return: Contents of the plist
    :rtype: dict or None if there is an error
    """

    try:
        plist = plistlib.readPlist(path_to_plist)
        log.debug("Entitlement Plist:%s", plist)
    except IOError:
        log.error("""There is no plist at path %s, check the codesign command
                  setup""", path_to_plist)
        return None
    return plist


def codesign_system_call_args(path_to_app):
    """ Returns the codesign call with the -dvvv flag and args

    :param path_to_app:  Path to the .app file
    :type key: str
    :returns: List with proper command line options to execute as a system
    call

    :rtype: list
    """
    if path_to_app is None:
        raise TypeError("path_to_app cannot be None")

    plist_path = support.get_value_from_config(support.ENTITLEMENTS_PLIST_PATH)
    # Prepend the path with a colon for the system call
    plist_path = str.format(":{0}", plist_path)
    codesign_call = ["codesign", "-dvvv", "--entitlements", plist_path,
                     path_to_app]
    log.debug("Codesign system call:%s", codesign_call)
    return codesign_call

# Remedial error messages, makes console output cleaner

# check_apns_server error message
REMEDIAL_APS_ACTION = """
Your AirshipConfig.plist APP_STORE_OR_AD_HOC_BUILD key is set to {0}.
Your APS server in the entitlements file is {1}.
The UA server is set for of {2}.
All of these values need to match, you need to review these settings.

Change one or more of the following settings to reconfigure:

1. APP_STORE_OR_AD_HOC_BUILD key, currently -> {3}, {entitle_server}
2. Mobile provisioning file, currently configured for {4}
3. Change Urban Airship configuration, which is {ua_server}
4. Change the app key and secret, which are:

Key:{app_key}
Secret:{app_secret}
"""

# key_secret fail message
AIRSHIP_CONFIG_PARSE_FAIL ="""
AirshipConfig.plist does not contain a bool or
string value for the APP_STORE_OR_AD_HOC key. Use PlistBuddy,
plutil, or Xcode to check the plist values"""

# check_bundle_id fail message
CHECK_BUNDLE_ID_FAIL = """Application bundle id {app_bundle} does not match
the bundle id configured on Urban Airship {ua_bundle}. Check the configuration"""

# check_aps_environment fail message
APS_ENVIRONMENT_KEY_FAIL = """
No APS environment string, the provisioning profile was not created with
push enabled, rebuild the profile with proper entitlements by enabling push
for your app, or simply recreating the provisioning profile after checking the
app settings on the Apple Developer portal. For reference, the bundle id of
your app is:\n{bundle_id}"""


# Support classes
class VerificationInformation(object):
    """Model object for data associated with build and verification."""

    def __init__(self, entitlements_plist=None,
                 airship_config_plist=None):
        """ Initialize object with entitlements and AirshipConfig plists

        :param entitlements_plist: Plist returned from codesign -dvvv command
        :type key: dict
        :param airship_config_plist: AirshipConfig.plist has a dictionary
        :type key: dict
        """

        self.entitlements_plist = entitlements_plist
        self.airship_config_plist = airship_config_plist
        # Bundle id with no app id
        self.bundle_id = None

    def __str__(self):
        return "\nEntitlements:\n{0}\nAirshipConfig:\n{1}\n".format(
            self.entitlements_plist,
            self.airship_config_plist)

    def airship_config_is_production(self):
        """Parse the AirshipConfig.plist and return the  APP_STORE_OR_AD_HOC
        value.

        Because of legacy reasons, and to support bad configurations, the
        value stored in the AirshipConfig.plist for the APP_STORE_OR_AD_HOC
        key could be either a bool or a string. This handles both cases,
        and returns a bool. If the value is not identifiable as a bool or
        string, the tool exits with a non zero exit value.

        :returns: Value for the APP_STORE_OR_AD_HOC key
        :rtype: bool
        """

        is_production = self.airship_config_plist[APP_STORE_OR_AD_HOC]
        # TODO
        # If is_production is not a bool, then this is a non xml plist, and
        # we look for a string YES/NO. Here we check for a string, and
        if not type(is_production) == bool:
            if type(is_production) == str:
                match = re.match('[Yy]', is_production)
                if match is None:
                    is_production = False
                else:
                    is_production = True
            else:
                # If not a bool or string, quit
                support.fail_log_message("AirshipConfig.plist not readable",
                    AIRSHIP_CONFIG_PARSE_FAIL)
                sys.exit(EXIT_FAILURE)
        return is_production

    def key_secret(self):
        """ Returns a named tuple with the key and secret

        Key and secret are parsed from the AirshipConfig.plist
        This will be either the production or development key/secret pair
        depending on the value of the APP_STORE_OR_AD_HOC_BUILD variable set
        in the plist.

        :returns: Named tuple with the values 'key','secret'
        :rtype: tuple
        """


        is_production = self.airship_config_is_production()

        if is_production:
            log.info("App is set for production in AirshipConfig")
            key = self.airship_config_plist[PRODUCTION_APP_KEY]
            secret = self.airship_config_plist[PRODUCTION_APP_SECRET]
        else:
            log.info("App is set for development in AirshipConfig")
            key = self.airship_config_plist[DEVELOPMENT_APP_KEY]
            secret = self.airship_config_plist[DEVELOPMENT_APP_SECRET]

        Auth = namedtuple('Auth', 'key secret')
        return Auth(key=key, secret=secret)

    def check_aps_environment(self):
        """APS environment check

        Check to see if the aps-environment keys exists

        :returns: True if the key exists, false otherwise
        :rtype: bool
        """

        try:
            full_bundle_id = self.entitlements_plist[ENTITLE_APP_ID_KEY]
        except KeyError:
            # TODO better error message
            support.fail_log_message("""Entitlements plist does not have a app id, this
            might be a bug in the script.""",
                """Email support@urbanairship.com""")
            return False
        try:
            self.entitlements_plist[ENTITLE_APS_ENV_KEY]
        except KeyError:
            msg = "No APS environment key"
            remedial = APS_ENVIRONMENT_KEY_FAIL.format(
                bundle_id=full_bundle_id)
            support.fail_log_message(msg, remedial)
            return False
        msg = "Environment is set properly for bundle id {0}".format(
            full_bundle_id)
        support.pass_log_message(msg)
        return True



    def check_apns_server(self, ua_verification_response):
        """ Check the production/development server in entitlements

        The API call to get data was authenticated with the key/secret pair
        related to the APP_STORE_OR_AD_HOC_BUILD value in the AirshipConfig
        plist. The API returns production or development based on those keys,
        this test checks that value against the value in the entitlements
        for the app.

        :param ua_verification_response: VerificationInformation object
        associated with this operation.

        :type key: str
        :returns: True if the servers match, false otherwise
        :rtype: bool
        """

        adhoc_or_prod = self.airship_config_is_production()

        if adhoc_or_prod:
            aps_env_description = PRODUCTION_SERVER
            app_key = self.airship_config_plist[PRODUCTION_APP_KEY]
            app_secret = self.airship_config_plist[PRODUCTION_APP_SECRET]
        else:
            aps_env_description = DEVELOPMENT_SERVER
            app_key = self.airship_config_plist[DEVELOPMENT_APP_KEY]
            app_secret = self.airship_config_plist[DEVELOPMENT_APP_SECRET]

        if ua_verification_response[UA_API_RESPONSE_PRODUCTION_KEY]:
            ua_aps_configuration = PRODUCTION_SERVER
        else:
            ua_aps_configuration = DEVELOPMENT_SERVER

        aps_environment = self.entitlements_plist[ENTITLE_APS_ENV_KEY]

        # Line up the servers
        if not ua_aps_configuration == aps_environment == aps_env_description:
            msg = "APS Environments don't match"
            # TODO fix these key/values up, so they are no more numbers or repetition
            remedial = REMEDIAL_APS_ACTION.format(aps_env_description,
                aps_environment, ua_aps_configuration,adhoc_or_prod,
                aps_environment, ua_aps_configuration, app_key=app_key,
                app_secret=app_secret, ua_server=ua_aps_configuration,
                entitle_server=aps_env_description)
            support.fail_log_message(msg, remedial)
            return False
        msg = "\nUrban Airship server is configured for: {0}\n".format(
            ua_aps_configuration)

        msg += "App is configured for: {0}".format(aps_environment)
        support.pass_log_message(msg)
        return True

    def check_bundle_id(self, ua_verification_response):
        """Check the bundle id for errors

        The API call returns the bundle ID associated with the app
        authenticated with the key/secret. Keep in mind, the bundle id in the
        entitlements is prepended with the App ID

        :param ua_verification_response: JSON response from UA API for this
        operation

        :type key: dict
        :returns: True is the bundle id is correct, false otherwise
        :rtype: bool
        """

        entitlements_bundle_id = self.entitlements_plist[ENTITLE_APP_ID_KEY]
        entitlements_bundle_id = entitlements_bundle_id.split('.')
        entitlements_bundle_id = entitlements_bundle_id[1:]
        entitlements_bundle_id = string.join(entitlements_bundle_id, '.')
        ua_bundle_id = ua_verification_response[UA_API_RESPONSE_BUNDLE_ID_KEY]
        log.info("Application Bundle id is: %s", entitlements_bundle_id)
        log.info("Urban Airship Configured App Bundle id is: %s", ua_bundle_id)

        if entitlements_bundle_id == ua_bundle_id:
            support.pass_log_message("Bundle id is correct")
            return True
        else:
           remedial = CHECK_BUNDLE_ID_FAIL.format(
               app_bundle=entitlements_bundle_id, ua_bundle=ua_bundle_id)
           support.fail_log_message("Bundle id is incorrect", remedial)
           return False

    def log_diagnostic_information(self):
        """Log out entitlements/config information for diagnostics
        """

        log.debug("ENTITLEMENTS:\n%s", self.entitlements_plist)
        log.debug("AIRSHIP_CONFIG:\n%s", self.airship_config_plist)
        log.debug("UA_API_RESPONSE:\n%s", support._ua_api_response)
