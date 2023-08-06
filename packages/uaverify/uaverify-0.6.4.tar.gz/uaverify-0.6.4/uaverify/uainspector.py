#!/usr/bin/python

import os
import sys
import argparse
import iossupport
import logging

from iossupport import VerificationInformation

class IosVerify(object):
    """ Verify the build with Urban Airship """

    def __init__(self):
        self.verification_info = None
        iossupport.clean()

    def execute_xcode_verify(self):
        """Execute all build verification tasks"""

        # Setup logger
        log = iossupport.log
        if self.diagnostic:
            iossupport.log.info("Setting up diagnostic logging")
            iossupport.setup_diagnostic_logging()

        # Extract entitlement info from app
        log.info("Executing codesign system call")
        success = iossupport.execute_codesign_system_call(
            self.application_path)
        if not success:
            log.error("Error in codesign system call")
            return False


        # Parse entitlement plist output
        entitlements_plist_path = iossupport.get_value_from_config(
            iossupport.ENTITLEMENTS_PLIST_PATH)
        entitlement_plist = iossupport.read_entitlement_plist_from_path(
            entitlements_plist_path)
        if entitlement_plist is None:
            log.error("Entitlement plist could not be read")
            return False

        # Read the AirshipConfig from the app
        airship_config_plist = iossupport.extract_airship_config_from_app(
            self.application_path)

        # Store entitlement and config info
        self.verification_info = VerificationInformation(
            entitlement_plist, airship_config_plist)
        iossupport.log.debug("Verification:%s", self.verification_info)

        # Check local entitlement settings and app configuration
        if not self.verification_info.check_aps_environment():
            return false

        # Make API verification request
        request = iossupport.get_verification_request(self.verification_info)
        response = iossupport.make_request_against_api(request)
        if response.error is not None:
            log.error("API verification request failed")
            return False
        iossupport.log.debug("Response %s", response)

        # API response dependent tests
        apns_server = self.verification_info.check_apns_server(response.json)
        if not apns_server:
            log.error("APNS server is not configured properly")
            return False

        bundle_id = self.verification_info.check_bundle_id(response.json)
        if not bundle_id :
            log.error("Bundle id mismatch")
            return False

        if self.diagnostic:
            # Print diagnostic info, this has the side effect of printing
            # to a file
            self.verification_info.log_diagnostic_information()

        return True


def main():
    """Parses args and executes appropriate tool"""

    # TODO make app path a non optional argument
    parser = argparse.ArgumentParser(
        description="Verify a build with Urban Airship",
        epilog=("""Extract the entitlements from a .app file, parse them, and
            check for errors. An API call is made to Urban Airship using the
            configured key/secret pair to return API app settings for
            comparison"""))

    parser.add_argument('application_path', type=str, help=(
        """"Path to the .app file for this app, described by the
        CODESIGNING_FOLDER_PATH environment variable in the Xcode build
        settings. These settings can be accessed by calling
        `xcodebuild -showBuildSettings -project ProjectName.xcodeproj` """))

    parser.add_argument('-d', '--diagnostic', action="store_true",
        help="Write out diagnostic information to a file")
    verify = IosVerify()
    # This appends the args

    parser.parse_args(namespace=verify)
    success = verify.execute_xcode_verify()
    # There is the possibility of a file logger
    logging.shutdown()
    if success:
        print("Successful verification")
        return iossupport.EXIT_SUCCESS
    else:
        print("Verification failed")
        return iossupport.EXIT_FAILURE


if __name__ == "__main__":
    sys.exit(main())
