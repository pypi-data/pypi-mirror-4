

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


"""Supporting methods for verifying an Android build from the project root
"""

import os
import fnmatch
import re

import support

from xml.etree import ElementTree as ET
from collections import namedtuple
from string import Template

import pdb

#logging
log_format = '%(asctime)s:%(levelname)s %(message)s'
# have to come up with a common name, instead of using the same logger
log = support.log

# Named tuple for search results
SearchResults = namedtuple("SearchResults", ["found", "not_found"])

#    For all of the ANDROID type values listed here, a lot of them need to be
#    namespaced. If you see android:name in the manifest, you'll need to call
#    manifest_attribute_key_with_namespace() to get the proper key value. This
#    simply prepends the key with the namespace, so it becomes
#    {http://schemas.android.com/apk/res/android}:key_name
#    which is what the XML library expects for the tree.get() command.
#    Example:
#    tree.get({namespace}:name) returns value associated with android:name

# Well known manifest namespace outlined here:
# http://developer.android.com/guide/topics/manifest/manifest-element.html
ANDROID_XMLNS = "http://schemas.android.com/apk/res/android"

# Take off method call
ANDROID_TAKE_OFF_METHOD_CALL = "takeOff"

# File names
ANDROID_MANIFEST_FILENAME = "AndroidManifest.xml"
ANDROID_AIRSHIP_PROPERTIES_FILENAME = "airshipconfig.properties"

# Airship Config file keys
ANDROID_CONFIG_DEV_APP_KEY = "developmentAppKey"
ANDROID_CONFIG_DEV_APP_SECRET_KEY = "developmentAppSecret"
ANDROID_CONFIG_PROD_APP_KEY = "productionAppKey"
ANDROID_CONFIG_PROD_APP_SECRET_KEY = "productionAppSecret"
ANDROID_CONFIG_TRANSPORT_KEY = "transport"
ANDROID_CONFIG_GCM_SENDER_KEY = "gcmSender"
ANDROID_CONFIG_IS_PROD_KEY = "inProduction"
ANDROID_CONFIG_ANALYTICS_ENABLED_KEY = "analyticsEnabled"

# Airship API response keys
UA_API_RESPONSE_PRODUCTION_KEY = "production"
UA_API_RESPONSE_PACKAGE_KEY = "android_package"
UA_API_RESPONSE_GCM_CONFIGURED = "gcm_is_configured"


# True/False string comparisons
STRING_TRUE = ["yes", "YES", "y", "Y", "Yes", "True", "true", "T"]
STRING_FALSE = ["no", "NO", "n", "N", "No", "False", "false", "F"]

# XML attribute keys
ANDROID_MANIFEST_PACKAGE_KEY = "package"
ANDROID_MANIFEST_PROTECTION_LEVEL_KEY = "protectionLevel"
ANDROID_MANIFEST_NAME_KEY = "name"
ANDROID_MANIFEST_PERMISSION_KEY = "permission"
ANDROID_MANIFEST_PROTECTION_LEVEL_SIGNATURE_KEY = "signature"
ANDROID_MANIFEST_PROVIDER_KEY = "provider"
ANDROID_MANIFEST_AUTHORITIES_KEY = "authorities"
ANDROID_MANIFEST_EXPORTED_KEY = "exported"
ANDROID_MANIFEST_MULTIPROCESS_KEY = "multiprocess"


# Android uses-permission declarations
ANDROID_USES_PERMISSION_INTERNET = "android.permission.INTERNET"
ANDROID_USES_PERMISSION_NETWORK_STATE = "android.permission.ACCESS_NETWORK_STATE"
ANDROID_USES_PERMISSION_VIBRATE = "android.permission.VIBRATE"
ANDROID_USES_PERMISSION_GET_ACCOUNTS = "android.permission.GET_ACCOUNTS"
ANDROID_USES_PERMISSION_WAKE_LOCK = "android.permission.WAKE_LOCK"
ANDROID_USES_PERMISSION_C2DM_RECEIVE = "com.google.android.c2dm.permission.RECEIVE"

# Android intent receivers
ANDROID_INTENT_RECEIVE = "com.google.android.c2dm.permission.RECEIVE"

# Optional not yet used in the script verification
ANDROID_PERMISSION_LOCATION = "android.permission.ACCESS_FINE_LOCATION"

# Required uses permissions as an iterable
_required_uses_permissions = [
    ANDROID_USES_PERMISSION_INTERNET,
    ANDROID_USES_PERMISSION_NETWORK_STATE,
    ANDROID_USES_PERMISSION_VIBRATE,
    ANDROID_USES_PERMISSION_GET_ACCOUNTS,
    ANDROID_USES_PERMISSION_WAKE_LOCK,
    ANDROID_USES_PERMISSION_C2DM_RECEIVE,
]

# Android permissions that related to messaging
ANDROID_PERMISSION_C2DM_SEND = "com.google.android.c2dm.permission.SEND"

# Intent permissions
ANDROID_INTENT_RECEIVE = "com.google.android.c2dm.intent.RECEIVE"
ANDROID_INTENT_REGISTRATION = "com.google.android.c2dm.intent.REGISTRATION"
ANDROID_INTENT_PACKAGE_REPLACED = "android.intent.action.PACKAGE_REPLACED"

# Iterable collection of intents, keep them in sync when adding new ones
_required_intents = [
    ANDROID_INTENT_RECEIVE,
    ANDROID_INTENT_REGISTRATION,
    ANDROID_INTENT_PACKAGE_REPLACED
]

# Package based permissions
#"com.urbanairship.push.sample.permission.C2D_MESSAGE
ANDROID_PACKAGE_BASED_PERMISSION_C2D_MESSAGE = "{package_name}.permission.C2D_MESSAGE"

# Receiver attributes
ANDROID_RECEIVER_CORE_RECEIVER = "com.urbanairship.CoreReceiver"
ANDROID_RECEIVER_GCM_PUSH_RECEIVER = "com.urbanairship.push.GCMPushReceiver"
ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION = "com.google.android.c2dm.permission.SEND"

# Iterable collection of receivers, keep them in sync
_required_receivers = [
    ANDROID_RECEIVER_CORE_RECEIVER,
    ANDROID_RECEIVER_GCM_PUSH_RECEIVER,
    ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION
]

# Content provider
ANDROID_CONTENT_PROVIDER_NAME = "com.urbanairship.UrbanAirshipProvider"
ANDROID_CONTENT_PROVIDER_AUTHORITIES = "{package_name}.urbanairship.provider"
ANDROID_CONTENT_PROVIDER_EXPORTED = "false"
ANDROID_CONTENT_PROVIDER_MULTIPROCESS = "multiprocess"

_required_provider_attributes = [
    ANDROID_CONTENT_PROVIDER_NAME,
    ANDROID_CONTENT_PROVIDER_AUTHORITIES,
    ANDROID_CONTENT_PROVIDER_EXPORTED,
    ANDROID_CONTENT_PROVIDER_MULTIPROCESS
]

MISSING_PROPERTY = """
Missing {property} property in properties file. Unable to create verification
request to use against the API. Check you airshipconfig.properties file for
errors"""


def get_verification_request(android_properties):
    """Get the verification request.

    :param android_properties: Dictionary of android properties
    :type key: dict
    :return: Request to make against the API
    :type key: urllib2.request
    """

    isProduction = android_properties.get(ANDROID_CONFIG_IS_PROD_KEY, None)
    if isProduction is None:
        log.info("airshipconfig.properties is missing isProduction key"
                 "Assuming development")
        isProduction = False

    try:
        if isProduction:
            appKey = android_properties[ANDROID_CONFIG_PROD_APP_KEY]
            appSecret = android_properties[ANDROID_CONFIG_PROD_APP_SECRET_KEY]
        else:
            appKey = android_properties[ANDROID_CONFIG_DEV_APP_KEY]
            appSecret = android_properties[ANDROID_CONFIG_DEV_APP_SECRET_KEY]
    except KeyError as error:
        log.error(MISSING_PROPERTY.format(property=error))
        return None

    return support.get_base_verification_request(appKey=appKey,
                                                 appSecret=appSecret)


def namespace_attribute_key(key, namespace=ANDROID_XMLNS):
    """Setup key with Android manifest namespace

    :param key: Key for required value
    :type key: str
    :param namespace: Namespace to use for key setup, defaults to ANDROID_XMLNS
    :type key: str
    :return: Key in the format {namespace}key
    :rtype: str
    """

    namespace_key_template = Template('{$namespace}$key')
    values = dict(namespace=namespace, key=key)
    return namespace_key_template.substitute(values)

def parse_manifest_in_directory(project_directory):
    """Recursively search the given directory for the AndroidManifest

    :param project_directory: Root directory of the project
    :return: Returns the first manifest found. If there are multiple manifests
        the result is one of those. Use parse_android_manifest for that
        situation.
    :rtype: xml.etree.ElementTree
    """

    path = find_file_from_dir(project_directory, ANDROID_MANIFEST_FILENAME)

    try:
        path = path.next()
        log.debug("AndroidManifest path {}".format(path))
    except StopIteration:
        log.error("No file name {} found in {}".format(ANDROID_MANIFEST_FILENAME,
                                                       project_directory))
        return None

    return parse_android_manifest(path)


def parse_android_manifest(manifest_path):
    """Parse the values of the android manifest

    :param manifest_path: Path to the root directory of the Android project
        to test

    :return: ElementTree with the contents of the AndroidManifest
    :rtype: xml.etree.ElementTree
    """

    try:
        tree = ET.parse(manifest_path)
    except ET.ParseError as parseError:
        log.error("Error parsing AndroidManifest {}".format(parseError.message))
        return None

    return tree


# Based on Stack Overflow answer, works well
def find_file_from_dir(base_dir, target_file):
    """Walk down from the root path, return all files with the filename

    :param base_dir: Base directory to start searching from.
    :type key: str
    :param target_file: file to search for
    :type key: str
    :return: Generator of files that match target_file
    :rtype: generator
    """

    for root, dirs, files in os.walk(base_dir, topdown=True):
        for filename in files:
            if fnmatch.fnmatch(filename, target_file):
                full_path_to_file = os.path.join(root, filename)
                yield full_path_to_file


def package_name_from_manifest(manifest_element_tree):
    """Extract the package name from the element tree representing the AndroidManifest

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :return: Package name
    :rtype: str
    """

    root = manifest_element_tree.getroot()
    return root.get(ANDROID_MANIFEST_PACKAGE_KEY)

MISSING_ATTRIBUTE = """
The AndroidManifest is missing the attribute
{missing_permission}
Please add the required permission to the manifest.
"""


def is_missing_uses_permissions(manifest_element_tree):
    """Check the permissions of type uses-permission

    Looking for similar xml:

    .. code-block:: xml

        <uses-permission android:name="android.permission.VIBRATE"/>
        <uses-permission android:name="com.google.android.c2dm.permission.RECEIVE"/>
        <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE"/>
        <uses-permission android:name="android.permission.WAKE_LOCK"/>
        <uses-permission android:name="android.permission.INTERNET"/>
        <uses-permission android:name="android.permission.GET_ACCOUNTS"/>

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :returns: True if there are missing permissions, false otherwise
    :rtype: bool
    """

    root = manifest_element_tree.getroot()
    permissions_list = []
    for permission in root.iter("uses-permission"):
        permissions_list.append(permission.get(namespace_attribute_key(
            ANDROID_MANIFEST_NAME_KEY)))

    search_results = \
        search_iterable_for_values(permissions_list, _required_uses_permissions)

    msg = "{}<uses-permission android:name=\"{}\"/>"
    for result in search_results.found:
        log.info(msg.format("Found: ", result))
    for result in search_results.not_found:
        log.error(msg.format("Missing permission: ", result))

    if len(search_results.not_found) is not 0:
        return True
    else:
        return False


def is_missing_package_dependent_permissions(manifest_element_tree,
                                             package_name):
    """Check for permissions that require the package name

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :param package_name: Android package name
    :return: True if correct permissions are present, false if not
    :rtype: bool
    """

    root = manifest_element_tree.getroot()
    c2dm_permission = ANDROID_PACKAGE_BASED_PERMISSION_C2D_MESSAGE.format(
        package_name=package_name)
    missing_permissions = []

    package_based_permission = \
        namespace_attribute_key(ANDROID_MANIFEST_NAME_KEY)
    package_based_permission_is_present = False

    # Looking for the
    # <permission android:name "package.name" android:protectionLevel:"signature"
    for permission in root.iter("permission"):
        name = permission.get(package_based_permission)
        protection_level = permission.get(namespace_attribute_key(
            ANDROID_MANIFEST_PROTECTION_LEVEL_KEY))
        if name == c2dm_permission and \
           protection_level == ANDROID_MANIFEST_PROTECTION_LEVEL_SIGNATURE_KEY:
            package_based_permission_is_present = True
            break

    if package_based_permission_is_present is False:
        msg = "<permission android:name \"{}\" android:protectionLevel:\"signature\"/>".format(
            c2dm_permission)
        missing_permissions.append(msg)
        msg = MISSING_ATTRIBUTE.format(missing_permission=msg)
        log.error(msg)

    # Looking for
    # <uses-permission android:name="package.foo.permission.C2D_MESSAGE" />
    package_based_permission_is_present = False
    for permission in root.iter("uses-permission"):
        name = permission.get(package_based_permission)
        if name == c2dm_permission:
            package_based_permission_is_present = True
            break

    if package_based_permission_is_present is False:
        msg = "<uses-permission android:name \"{}\"/>".format(c2dm_permission)
        missing_permissions.append(msg)
        msg = MISSING_ATTRIBUTE.format(missing_permission=msg)
        log.error(msg)

    if len(missing_permissions) is not 0:
        return True
    else:
        return False


def is_missing_receiver_attributes(manifest_element_tree):
    """Check required application receiver attributes

    Looking for similar XML

    .. code-block:: xml

        <receiver android:name="com.urbanairship.push.GCMPushReceiver" android:permission="com.google.android.c2dm.permission.SEND">
        <receiver android:name="com.urbanairship.push.GCMPushReceiver" android:permission="com.google.android.c2dm.permission.SEND">
        <receiver android:name="com.google.android.c2dm.permission.SEND" />

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :return: True if required permissions are present, false if not
    :rtype: bool
    """

    # This is different than the majority of the settings.
    # There are two elements we are interested in, and one of the two elements
    # has two values that we need

    root = manifest_element_tree.getroot()
    found_receiver_attributes = []
    core_receiver = ANDROID_RECEIVER_CORE_RECEIVER
    # The xml has a namespace, each time you see android in the xml, it's really
    # {http://schemas.android.com/apk/res/android}
    name = namespace_attribute_key(ANDROID_MANIFEST_NAME_KEY)

    # Search for <receiver android:name="com.urbanairship.CoreReceiver" />,
    # add it to the found list
    for receiver_attrib in root.iter("receiver"):
        attribute = receiver_attrib.get(name)
        if attribute == core_receiver:
            found_receiver_attributes.append(attribute)

    # Search for <receiver android:name="com.urbanairship.push.GCMPushReceiver"
    # android:permission="com.google.android.c2dm.permission.SEND">
    # and check both values. Just add the android:name value if found to list
    # of found values
    gcm_push_receiver = ANDROID_RECEIVER_GCM_PUSH_RECEIVER
    target_permission = "<receiver android:name=\"com.urbanairship.push.GCMPushReceiver\" android:permission=\"com.google.android.c2dm.permission.SEND/\">"
    for receiver_attrib in root.iter("receiver"):
        value = receiver_attrib.get(name)
        if value == gcm_push_receiver:
            permission_send_key = namespace_attribute_key(
                ANDROID_MANIFEST_PERMISSION_KEY)
            permission_send = receiver_attrib.get(permission_send_key)
            if permission_send == ANDROID_PERMISSION_C2DM_SEND:
                log.info("Found: %s in manifest" %
                         target_permission)
                # Add both values here, so that you get a positive result if
                # and only if both values exist in the correct place
                found_receiver_attributes.append(permission_send)
                found_receiver_attributes.append(value)
                break

    search_results = search_iterable_for_values(found_receiver_attributes,
                                                _required_receivers)

    # Log results, formatted to look like XML
    core_receiver_xml = "{}<receiver android:name=\"{}\" />"
    receiver_xml = "{}<receiver android:name=\"{}\" android:permission=\"{}/\">"

    for result in search_results.found:
        if result == ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION:
            log.info(core_receiver_xml.format("Found: ", ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION))
        if result == ANDROID_RECEIVER_GCM_PUSH_RECEIVER:
            msg = receiver_xml.format("Found: ",
                                      ANDROID_RECEIVER_GCM_PUSH_RECEIVER,
                                      ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION)
            log.info(msg)

    for result in search_results.not_found:
        if result == ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION:
            log.error(core_receiver_xml.format("Missing: ", ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION))
        if result == ANDROID_RECEIVER_GCM_PUSH_RECEIVER:
            msg = receiver_xml.format("Missing: ",
                                      ANDROID_RECEIVER_GCM_PUSH_RECEIVER,
                                      ANDROID_RECEIVER_GCM_PUSH_RECEIVER_PERMISSION)
            log.error(msg)

    if len(search_results.not_found) is not 0:
        return True
    else:
        return False


def is_missing_action_attributes(manifest_element_tree):
    """Check required intent filters have the required actions

    Looking for the similar xml

    .. code-block:: xml

        <action android:name="com.google.android.c2dm.intent.REGISTRATION"/>
        <action android:name="android.intent.action.PACKAGE_REPLACED"/>
        <action android:name="com.google.android.c2dm.intent.RECEIVE"/>

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :return: True if filters are missing, false otherwise
    :rtype: bool
    """

    root = manifest_element_tree.getroot()
    action_values = []
    for attribute in root.iter("intent-filter"):
        for action in attribute.findall("action"):
            name = namespace_attribute_key(
                ANDROID_MANIFEST_NAME_KEY)
            value = action.get(name)
            if value is not None:
                action_values.append(value)

    search_results = \
        search_iterable_for_values(action_values, _required_intents)

    msg = "{}<action android:name=\"{}\"\>"
    for found in search_results.found:
        log.info(msg.format("Found: ", found))
    for not_found in search_results.not_found:
        log.error(msg.format("Missing intent action:", not_found))

    if len(search_results.not_found) is not 0:
        return True
    else:
        return False

MISSING_PROVIDER_FIX = """
<provider android:name="com.urbanairship.UrbanAirshipProvider"
    android:authorities="{package_name}.urbanairship.provider"
    android:exported="false"
    android:multiprocess="true" />
"""


def is_missing_android_provider_attribute(manifest_element_tree, package_name):
    """Check required provider attribute

    Checks for the 4 required attributes (name, authorities, exported, and
    multiprocess) and the corresponding values

    :param manifest_element_tree: Tree for the AndroidManifest
    :type key: ElementTree
    :param package_name: Package name for project
    :type key: str
    :return: True if provider is correct, false otherwise
    :rtype: bool
    """

    root = manifest_element_tree.getroot()
    provider_keys_values = dict()
    attribute_name = namespace_attribute_key(
        ANDROID_MANIFEST_NAME_KEY)

    for attribute in root.iter(ANDROID_MANIFEST_PROVIDER_KEY):
        name = attribute.get(attribute_name)
        if name == ANDROID_CONTENT_PROVIDER_NAME:

            value = attribute.get(namespace_attribute_key(
                ANDROID_MANIFEST_AUTHORITIES_KEY))
            provider_keys_values[ANDROID_MANIFEST_AUTHORITIES_KEY] = value

            value = attribute.get(namespace_attribute_key(
                ANDROID_MANIFEST_EXPORTED_KEY))
            provider_keys_values[ANDROID_MANIFEST_EXPORTED_KEY] = value

            value = attribute.get(
                namespace_attribute_key(ANDROID_MANIFEST_MULTIPROCESS_KEY))
            provider_keys_values[ANDROID_MANIFEST_MULTIPROCESS_KEY] = value

            break

    required_attributes = required_provider_attributes(package_name)
    if provider_keys_values == required_attributes:
        return False
    else:
        msg = "Missing permissions for provider, the permission should have " \
              "the following structure"
        log.error(msg)
        log.error(MISSING_PROVIDER_FIX.format(package_name=package_name))
        return True


def required_provider_attributes(package_name):
    """Creates the required attributes for the provider element

    The provider element has 4 attributes, name, authorities, exported and
    multiprocess. The value of the authorities attribute is dependent on the
    package name. This method returns the three values other than the name,
    since the name is required to get the three values.

    :param package_name: The package name used to create the authorities value
    :type key: str
    :return: Dictionary with the 3 attribute values
    :rtype: dict
    """

    required_values = dict()
    required_values[ANDROID_MANIFEST_EXPORTED_KEY] = "false"
    required_values[ANDROID_MANIFEST_MULTIPROCESS_KEY] = "true"
    authority = "{}.urbanairship.provider".format(package_name)
    required_values[ANDROID_MANIFEST_AUTHORITIES_KEY] = authority

    return required_values

PACKAGE_NAME_MISMATCH = """
"Package name in manifest {app} does not match {server} on UA servers"
"""


def is_airship_configured_properly(airship_api_response,
                                   airship_config_properties,
                                   application_package_name):
    """Compare the UA server configuration with airshipconfig.properties

    Also checks the package name in the AndroidManifest against the API
    response.

    :param airship_api_response: The json response from UA
    :type key: dict
    :param airship_config_properties: Properties from the
        airshipconfig.properties file
        
    :type key: dict
    :param application_package_name: Package name for the application
    :type key: str
    :return: True if app is configured properly, false otherwise
    :rtype: bool
    """

    tests = []
    server_package_name = airship_api_response[UA_API_RESPONSE_PACKAGE_KEY]
    if server_package_name != application_package_name:

        log.info(PACKAGE_NAME_MISMATCH.format(app=application_package_name,
                                              server=server_package_name))
        tests.append(False)
    else:
        log.info("Package name is configured on UA and matches")

    if airship_api_response[UA_API_RESPONSE_GCM_CONFIGURED] is False:
        log.error("GCM is not configured on Urban Airship servers")
        tests.append(False)
    else:
        log.info("GCM is configured on the UA servers")

    # XOR by converting False/True to 0/1 with bool(Bool)
    isServerProduction = airship_api_response[UA_API_RESPONSE_PRODUCTION_KEY]
    isAppProduction = airship_config_properties[ANDROID_CONFIG_IS_PROD_KEY]

    if bool(isServerProduction) ^ bool(isAppProduction):
        log.error("There is a configuration error for production/development")
        log.error("airshipconfig.properties inProduction is %s" %
                  isAppProduction)
        log.error("UA Server Production value is %s" % isServerProduction)
        tests.append(False)
    else:
        log.info("Server and application production values are correct")

    if False in tests:
        return False
    else:
        return True


def read_properties_file(root_directory):
    """Read the airshipconfig.properties file

    This assumes that there is a single airshipconfig.properties file, and it
    is somewhere in the project directory, or a subdirectory of the project
    directory. This stops at the first instance of a property file. The file
    is parsed with rudimentary string splitting based on the "=" character

    :param root_directory: Directory to search from
    :return: Contents of properties file, None on error
    :rtype: dict
    """

    path_iterator = find_file_from_dir(root_directory,
                                       ANDROID_AIRSHIP_PROPERTIES_FILENAME)
    try:
        airship_config_file = path_iterator.next()
    except StopIteration:
        airship_config_file = None

    if airship_config_file is None:
        log.error("No config file found. Searched for {} from root {}".format(
            ANDROID_AIRSHIP_PROPERTIES_FILENAME,  root_directory))
        return None
    else:
        properties = dict()
        for line in open(airship_config_file, "r"):
            key_value = line.strip().split("=")
            # Skip comments
            if "#" in key_value[0]:
                continue
            # Only go for key/value pairs
            if len(key_value) != 2:
                continue
            key = key_value[0].strip()
            value = key_value[1].strip()
            log.debug("Adding config properties key:{} val:{}".format(key, value))
            # strip keys and values of whitespace
            properties[key] = value
        # TODO this will throw an exception if the key is not present
        match = None
        try:
            match = re.match('[Yy]', properties[ANDROID_CONFIG_IS_PROD_KEY])
        except KeyError:
            log.info("Missing isProduction key in AirshipConfig.properties. "
                     "Defaulting to development.")
        if match is None:
            properties[ANDROID_CONFIG_IS_PROD_KEY] = False
        else:
            properties[ANDROID_CONFIG_IS_PROD_KEY] = True

    return properties


def search_iterable_for_values(values, targets):
    """Takes a collection of values an then searches it for all targets.

    :param values: Values to be searched
    :param targets: Values to look for in the collection

    :return: Tuple of values in the order of Found, Missing. Both
    :rtype: tuple
    """

    values = set(values)
    targets = set(targets)
    log.debug("Searching for\n%s\n in \n%s\n", targets, values)
    targets_in_values = values.intersection(targets)
    targets_missing_from_values = targets.difference(values)

    return SearchResults(found=targets_in_values,
                         not_found=targets_missing_from_values)


# TODO add support for manually implementing reports with onStart/onStop
def is_analytics_implemented(root_path):
    """Recursively search for java files that use Android reports

    Checks for classes that extend InstrumentedActivity or
    InstrumentedListActivity and if analytics are enabled. Will also return
    false if there is no config file, or there is a parse error

    :param root_path: Root path to begin search
    :return: True if classes exist an analytics are not disabled
    :rtype: bool
    """

    airship_config = read_properties_file(root_path)

    # Analytics is not enabled in this case, and everything is probably broken
    # anyway
    if airship_config is None:
        log.error("No airshipconfig.properties found at path %s" % root_path)
        return False

    is_analytics_enabled = True
    is_analytics_enabled_string = None

    # There is a good chance this key has been omitted from the config file
    try:
        is_analytics_enabled_string = \
            airship_config[ANDROID_CONFIG_ANALYTICS_ENABLED_KEY]
    except KeyError:
        log.info(
            "analyticsEnabled key not found in properties file, "
            "defaulting to true")

    if is_analytics_enabled_string is not None:
        if is_analytics_enabled_string in STRING_TRUE:
            is_analytics_enabled = True
        else:
            is_analytics_enabled = False

    if is_analytics_enabled is not True:
        log.info(
            "Analytics has been purposefully disabled in "
            "airshipconfig.properties")

        return False

    java_file_generator = find_file_from_dir(root_path, "*.java")

    files_with_analytics = list()
    instrumented_activity_pattern = re.compile("extends\s+InstrumentedActivity")
    instrumented_activity_list_pattern = \
        re.compile("extends\s+InstrumentedListActivity")

    for java_file_path in java_file_generator:

        with open(java_file_path, "r") as java_file:

            for line in java_file:

                if instrumented_activity_pattern.search(line) is not None:
                    log.info("Found instrumented activity at path %s" %
                             java_file_path)
                    files_with_analytics.append(java_file_path)

                if instrumented_activity_list_pattern.search(line) is not None:
                    log.info("Found instrumented list activity at path %s" %
                             java_file_path)
                    files_with_analytics.append(java_file_path)

    if len(files_with_analytics) == 0 and is_analytics_enabled is True:
        log.error("Analytics are enabled, but no files extend an "
                  "instrumented activity")

        return False

    return True


def is_takeoff_called(root_path):
    """Check to see if takeOff is called in code

    Checks for a class that extends Application and contains a call to
    takeOff: This will return true at the first match of a class that extends
    Activity and calls takeOff

    :param root_path: Recursively search from this directory
    :return: True if takeOff is present, false otherwise
    :rtype: bool
    """

    java_file_generator = find_file_from_dir(root_path, "*.java")
    take_off_found = False

    for java_file_path in java_file_generator:
        application_found = False

        # Look for java class that extends Application
        with open(java_file_path, "r") as java_file:
            pattern = re.compile("extends\s+Application")
            for line in java_file:
                if pattern.search(line) is not None:
                    log.info("Searching {} for call to takeOff".format(
                        java_file_path))
                    application_found = True
                    break

        # If the class extends Application, check for takeOff
        if application_found is True:
            with open(java_file_path, "r") as java_file:
                pattern = re.compile("takeOff")
                for line in java_file:
                    if pattern.search(line) is not None:
                        take_off_found = True
                        log.info("Found takeOff in file {} in line {}".format(
                            java_file_path, line.strip()))

        if take_off_found is True:
            break

    return take_off_found
