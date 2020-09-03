#!/usr/bin/env python3
"""rotate your AWS IAM key"""
# pipenv run python s3ver_make.py <usermap>

import os
import random # ??
import re
from shutil import copy2
import string
import sys
#import time
import configparser
import json
import boto3 # pylint: disable=import-error
import pprint # pylint: disable=unused-import

def credentials_backup_filename():
    mainfile = credentials_filename()
    return mainfile + ".bak"

def credentials_filename():
    home = os.environ.get('HOME')
    filename = "%s/.aws/credentials" % (home)
    return filename

def backup_credentials():
    copy2(credentials_filename(), credentials_backup_filename())

def read_credentials():
    creds = configparser.ConfigParser()
    creds.read(credentials_filename())
    return creds

def rotate_key():
    iam = boto3.client('iam') # TODO: try resource for this stuff
    iamr = boto3.resource('iam')

    user = iamr.CurrentUser().user_name
    iamuser = iamr.User(user)

    # tags
    user_resp = iam.get_user(UserName=user)['User']
    tags_print = ""
    if 'Tags' in user_resp:
        for tagrec in user_resp['Tags']:
            tags_print += "%s=%s " % (tagrec['Key'], tagrec['Value'])

        tags_print = re.sub(r' $', '', tags_print)

    print("Welcome, %s. (%s)" % (user,tags_print))

    # get current credentials from file
    creds_file = credentials_filename()
    creds = read_credentials()
    creds_count = len(creds.sections())
    print("You have %d creds in `%s`." % (creds_count, creds_file))
    profiles = {} # map key ids to their corresponding profile
    for profile in creds.sections():
        profiles[creds[profile]["aws_access_key_id"]] = profile

    # get current key from IAM
    iam_keys_resp = iam.list_access_keys(UserName=user)
    iam_keys = iam_keys_resp['AccessKeyMetadata']
    update_profile = None;
    if not iam_keys:
        print("IAM user %s has no keys!  There is nothing to do here. :)" % (user))
        return # TODO: just create a new key
    else:
        print("You have %d key(s) in IAM for %s:" % (len(iam_keys), user))
        for k in iam_keys:
            # when was it last used?
            last_used_resp = iam.get_access_key_last_used(
                AccessKeyId=k['AccessKeyId'])['AccessKeyLastUsed']
            if 'LastUsedDate' in last_used_resp:
                last_used = "on %s for %s" % (
                    last_used_resp['LastUsedDate'], last_used_resp['ServiceName'])
            else:
                last_used = "never"

            prof = "none"
            if k['AccessKeyId'] in profiles:
                prof = profiles[k['AccessKeyId']]
                update_profile = prof

            print("- %s key %s created %s used %s profile %s" % (
                k['Status'], k['AccessKeyId'], k['CreateDate'], last_used, prof
                ))

    if len(iam_keys) > 1:
        print("Not handling more than one key yet either. :)")
        return

    backup_credentials()

    access_key_pair = iamuser.create_access_key_pair()

    # TODO: validate keypair before writing to disk

    # rewrite credentials file with new credentials
    creds[update_profile]["aws_access_key_id"] = access_key_pair.id
    creds[update_profile]["aws_secret_access_key"] = access_key_pair.secret

    with open(credentials_filename(), 'w') as destfile:
        creds.write(destfile)

    print("%s rewritten" % (credentials_filename()))

    # TODO: deactivate old key

if __name__ == "__main__":
    rotate_key()
