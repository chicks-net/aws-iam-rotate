#!/usr/bin/env python3
"""rotate your AWS IAM key"""
# pipenv run python s3ver_make.py <usermap>

import random # ??
import re
import string
import sys
#import time
import json
import boto3 # pylint: disable=import-error
import pprint # pylint: disable=unused-import

def get_all_users(iam):
    """get all IAM users, return a list of usernames"""
    iam_users = []
    paginator = iam.get_paginator('list_users')
    for page in paginator.paginate():
        for user in page['Users']:
            iam_users.append(user['UserName'])

    print("users retrieved...")
    return iam_users

def print_iam_user(iam, user, tags_print):
    """print out an IAM user with key details"""
    try:
        # keys
        iam_keys_resp = iam.list_access_keys(UserName=user)
        iam_keys = iam_keys_resp['AccessKeyMetadata']
        if not iam_keys:
            print("IAM user %s (%s) has no keys! :)" % (user, tags_print))
        else:
            for k in iam_keys:
                last_used_resp = iam.get_access_key_last_used(
                    AccessKeyId=k['AccessKeyId'])['AccessKeyLastUsed']
                if 'LastUsedDate' in last_used_resp:
                    last_used = "on %s for %s" % (
                        last_used_resp['LastUsedDate'], last_used_resp['ServiceName'])
                else:
                    last_used = "never"

                print("IAM user %s (%s) has %s key %s created %s used %s" % (
                    user, tags_print, k['Status'], k['AccessKeyId'], k['CreateDate'], last_used
                    ))

    except iam.exceptions.NoSuchEntityException:
        print('no user %s...' % (user))

def list_iam_keys():
    """print out all IAM users, their keys, and key details"""
    iam = boto3.client('iam')

    iam_users = get_all_users(iam)
    for user in sorted(iam_users):
        # tags
        user_resp = iam.get_user(UserName=user)['User']
        tags_print = ""
        if 'Tags' in user_resp:
            for tagrec in user_resp['Tags']:
                tags_print += "%s=%s " % (tagrec['Key'], tagrec['Value'])

            tags_print = re.sub(r' $', '', tags_print)

        print_iam_user(iam, user, tags_print)

def list_s3_buckets(s3):
    response = s3.list_buckets()     # Call S3 to list current buckets

    # Get a list of all bucket names from the response
    buckets = [bucket['Name'] for bucket in response['Buckets']]

    #print("Bucket List: %s" % buckets)
    return buckets

def iam_create_user(iam,user_name):
    pp = pprint.PrettyPrinter(indent=4)
    print("... Creating IAM user " + user_name)

    iam.create_user(UserName=user_name)

    # get keys
    access_key = iam.create_access_key(UserName=user_name)
    key_id = access_key['AccessKey']['AccessKeyId']
    key_secret = access_key['AccessKey']['SecretAccessKey']

    # cache a copy for testing
    with open("/Users/chicks/.aws/credentials","a") as f:
        print("", file=f) # blank line
        print("[" + user_name + "]", file=f)
        print("aws_access_key_id = " + key_id, file=f)
        print("aws_secret_access_key = " + key_secret, file=f)

    # TODO??: implement adding to group


    return key_id, key_secret

def rotate_key():
    iam = boto3.client('iam')
    iamr = boto3.resource('iam')

    user = iamr.CurrentUser().user_name

    # tags
    user_resp = iam.get_user(UserName=user)['User']
    tags_print = ""
    if 'Tags' in user_resp:
        for tagrec in user_resp['Tags']:
            tags_print += "%s=%s " % (tagrec['Key'], tagrec['Value'])

        tags_print = re.sub(r' $', '', tags_print)

    print_iam_user(iam, user, tags_print)

if __name__ == "__main__":
    rotate_key()
