#!/usr/bin/env python3
"""rotate your AWS IAM key"""
# pipenv run python s3ver_make.py <usermap>

import configparser
import os
#import pprint # pylint: disable=unused-import
import re
from shutil import copy2
import sys
import boto3 # pylint: disable=import-error

def credentials_backup_filename():
    """filename for credientials backup"""
    mainfile = credentials_filename()
    return mainfile + ".bak"

def credentials_filename():
    """filename for credientials primary"""
    home = os.environ.get('HOME')
    filename = "%s/.aws/credentials" % (home)
    return filename

def backup_credentials():
    """perform backup of credentials file"""
    copy2(credentials_filename(), credentials_backup_filename())

def read_credentials():
    """read the credentials file using configparser"""
    creds = configparser.ConfigParser()
    creds.read(credentials_filename())
    return creds

def print_tags(iamuser):
    """return string of tags for user"""
    tags_print = ""
    for tagrec in iamuser.tags:
        tags_print += "%s=%s " % (tagrec['Key'], tagrec['Value'])

    tags_print = re.sub(r' $', '', tags_print)
    return tags_print

def get_keylist(user):
    """get list of IAM keys for user"""
    iam = boto3.client('iam') # I tried boto resources for this, but I couldn't get it to work.

    # get current key from IAM
    iam_keys_resp = iam.list_access_keys(UserName=user)
    iam_keys = iam_keys_resp['AccessKeyMetadata']

    return iam_keys

def print_keylist(user, profiles):
    """print list of IAM keys for user with last access details"""
    iam = boto3.client('iam') # I tried boto resources for this, but I couldn't get it to work.
    iam_keys = get_keylist(user)
    update_profile = None
    if iam_keys:
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

            # can we match it to a profile from your creds file?
            prof = "none"
            if k['AccessKeyId'] in profiles:
                prof = profiles[k['AccessKeyId']]
                update_profile = prof

            print("    - %s key %s matches profile %s" % (k['Status'], k['AccessKeyId'], prof))
            print("\t(created %s used %s)" % (k['CreateDate'], last_used))

        return update_profile
    else:
        raise Exception("IAM user %s has no keys!  There is nothing to do here. :)" % (user))

def validate_keypair(username,keypair):
    """check keypair to make sure it works"""
    #keypair_resource = iamr.AccessKeyPair(user, access_key_pair.id, access_key_pair.secret)

    # might break considering https://github.com/boto/boto3/issues/2133
    #if keypair_resource.status == "Active":
    #    # How can I better validate the keypair?
    #    print("Your key looks ok.")
    #else:
    #    print("Your key looks problematic: %s." % (keypair_resource.status))
    #    print("Your old key should still work since we didn't deactivate it.")
    #    raise Exception("This looks bad to write to disk so original creds file is left intact.")

    key_resource = iamr.AccessKey(username, keypair.id)
    if key_resource.status == "Active":
        print("Your key looks ok.")
    else:
        print("Your key looks problematic: %s." % (key_resource.status))
        print("Your old key should still work since we didn't deactivate it.")

    # next try: aws sts get-access-key-info --access-key-id $keyid

def rotate_key():
    """rotate the user's IAM key"""
    iamr = boto3.resource('iam')
    user = iamr.CurrentUser().user_name
    iamuser = iamr.User(user)
    print("Welcome, %s. (%s)" % (user, print_tags(iamuser)))

    # get current credentials from file
    creds = read_credentials()
    creds_count = len(creds.sections())
    print("You have %d creds in `%s`." % (creds_count, credentials_filename()))

    # map key ids to their corresponding profile
    profiles = {}
    for profile in creds.sections():
        profiles[creds[profile]["aws_access_key_id"]] = profile

    # how many keys there are determines what we can do
    iam_keys = get_keylist(user)
    if not iam_keys:
        print("IAM user %s has no keys!  There is nothing to do here. :)" % (user))
        return
    elif len(iam_keys) > 1:
        print_keylist(user, profiles)
        print("Not handling more than one key yet either. :)")
        return
    else:
        update_profile = print_keylist(user, profiles)

    old_keyid = creds[update_profile]["aws_access_key_id"]
    oldkey_resource = iamr.AccessKey(user, old_keyid)
    backup_credentials() # the file

    # create new key
    access_key_pair = iamuser.create_access_key_pair()

    # validate keypair before writing to disk
    validate_keypair(user,access_key_pair)

    # rewrite credentials file with new credentials
    creds[update_profile]["aws_access_key_id"] = access_key_pair.id
    creds[update_profile]["aws_secret_access_key"] = access_key_pair.secret

    with open(credentials_filename(), 'w') as destfile:
        creds.write(destfile)

    print("%s rewritten" % (credentials_filename()))

    # TODO: deactivate old key
    #oldkey_resource.deactivate()

if __name__ == "__main__":
    rotate_key()
