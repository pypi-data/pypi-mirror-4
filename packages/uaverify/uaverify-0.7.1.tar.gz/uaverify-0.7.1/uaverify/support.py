"""Common functionality for iOS and Android verification"""

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

import ConfigParser
import json
import logging
import urllib2
import urlparse
import base64
import sys
import os

from datetime import datetime
from collections import namedtuple

# Logging name
UA_LOGGER = "com.urbanairship.uaverify"

# UA API URLS
UA_API_BASE = "api_base"
UA_API_PATH = "api_path"

# Exit status
EXIT_SUCCESS = 0
EXIT_FAILURE = 1

# Configuration values
DEFAULT_CONFIG_NAME = "ua_inspection.cfg"
UA_SECTION = "ua_config"
LOG_LEVEL = "log_level"
ENTITLEMENTS_PLIST_PATH = "entitlement_plist_path"
AIRSHIP_CONFIG_PLIST = "airship_config_plist"

# Response for UA API requests
Response = namedtuple('Response', ["json", "error"])

# Configuration parsing
# Load configuration file, or log an error
config_parser = ConfigParser.ConfigParser()
config_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_path, DEFAULT_CONFIG_NAME)

if not os.path.exists(config_path):
    logging.error("No config file found at path %s", config_path)
    sys.exit(EXIT_FAILURE)

config_parser.read(config_path)

# Store the API response to use in diagnostic print outs
_ua_api_response = None


def get_base_verification_request(appKey, appSecret):
    """Get the verification request.

    The request is setup with
    basic auth headers authenticated with the appKey and appSecret

    :param appKey: The application key
    :type key: str
    :param appSecret: The application secret
    :type key: str
    :return: Pre authenticated http request
    :rtype: urllib2.Request
    """

    base_url = get_value_from_config(UA_API_BASE)
    api_url = get_value_from_config(UA_API_PATH)
    ua_url = urlparse.urljoin(base_url, api_url)
    log.info("URL for verification call %s", ua_url)
    basic_auth = "{0}:{1}".format(appKey, appSecret)
    basic_auth_encoded = base64.encodestring(basic_auth)
    pre_auth = {'Authorization': "Basic %s" % basic_auth_encoded}
    log.debug("Headers for UA verification request %s", pre_auth)
    return urllib2.Request(ua_url, headers=pre_auth)


def get_value_from_config(key, section=UA_SECTION):
    """Returns a configuration value for the given key.

    Return the value associated with the key
    from the configuration file. Uses the default
    section defined by UA_SECTION unless overridden
    See ConfigParser for more details

    :param key: Key associated with value
    :type key: str
    :param section: Section to retrieve value from
    :type section: str
    """

    return config_parser.get(section, key)


# Logging setup

# Timestamp and log formatting
# LogLevel
log_format = '%(asctime)s:%(levelname)s %(message)s'
logging.basicConfig(format=log_format)
log = logging.getLogger(UA_LOGGER)
log.setLevel(get_value_from_config(LOG_LEVEL))


def make_request_against_api(request):
    """Make a request against the UA API

    Returns a named tuple with response data as JSON and a possible error
    object which is either an HTTPError, 401,500, etc or a URLError which
    most likely occurs when there is no connection. All other errors will
    exception out.

    :param request: Request to make
    :type key: urllib2.Request
    :return: Named tuple in the form (response, error)
    :rtype: namedtuple
    """

    error = None
    json_data = None

    try:
        raw_response = urllib2.urlopen(request)
        json_data = json.load(raw_response)

    except urllib2.HTTPError as http_error:
        log.error("HTTP error %s with code %d", http_error.message,
                  http_error.code)
        error = http_error

    except urllib2.URLError as url_error:
        log.error("URL error, are you connected to the internet?")
        log.error("URL error message %s", url_error)
        error = url_error

    # Saving UA API response in case diagnostic logging is used.
    _ua_api_response = Response(json=json_data, error=error)
    return _ua_api_response


def setup_diagnostic_logging():
    """Adds a file handler to the logger object to output information

    Also attempts to prepend the diagnostic log file with entitlement and
    configuration information
    """

    log.setLevel(logging.DEBUG)
    now = datetime.now()
    filename = now.strftime("ua_verify_diagnostic_%d%b%y_%X.txt")
    path = os.getcwd()
    file_path = os.path.join(path, filename)
    log.info("Diagnostic log path %s", file_path)
    log_handler = logging.FileHandler(file_path)
    log_handler.setLevel(logging.DEBUG)
    log.addHandler(log_handler)
