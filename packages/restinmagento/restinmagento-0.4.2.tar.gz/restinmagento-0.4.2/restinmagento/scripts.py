"""CLI scripts.
"""

import argparse
import sys
import urlparse

import requests
from requests_oauthlib import OAuth1


def handle_error(response):
    sys.stdout.write("Failed to obtain a temporary token." + '\n')
    sys.stdout.write("HTTP error code is: %s %s" % (response.status_code,
        response.reason) + '\n')
    if response.status_code != 404:
        sys.stdout.write("HTTP response body: %s" % response.text + '\n')


def tmptoken():
    parser = argparse.ArgumentParser(description='Temporary token')
    parser.add_argument('--url', type=unicode, help='Url to request token')
    parser.add_argument('--clientkey', type=unicode)
    parser.add_argument('--clientsecret', type=unicode)
    args = parser.parse_args()
    oauth = OAuth1(args.clientkey, client_secret=args.clientsecret, callback_uri=args.url)
    response = requests.post(url=args.url, auth=oauth)
    sys.stdout.write('\n')
    if response.status_code == 200:
        sys.stdout.write("Obtained a temporary token." + '\n')
        params = urlparse.parse_qs(response.content)
        sys.stdout.write("Temporary key: %s" % params['oauth_token'][0] + '\n')
        sys.stdout.write("Temporary secret: %s" % params['oauth_token_secret'][0] + '\n')
    else:
        handle_error(response)
    sys.stdout.write('\n')


def resourcetoken():
    parser = argparse.ArgumentParser(description='access token')
    parser.add_argument('--url', type=unicode, help='url to access token')
    parser.add_argument('--clientkey', type=unicode)
    parser.add_argument('--clientsecret', type=unicode)
    parser.add_argument('--tmpkey', type=unicode)
    parser.add_argument('--tmpsecret', type=unicode)
    parser.add_argument('--verifier', type=unicode)
    args = parser.parse_args()
    oauth = OAuth1(client_key=args.clientkey, client_secret=args.clientsecret,
            resource_owner_key=args.tmpkey,
            resource_owner_secret=args.tmpsecret,
            verifier=args.verifier)

    response = requests.post(url=args.url, auth=oauth)
    sys.stdout.write('\n')
    if response.status_code == 200:
        sys.stdout.write("Obtained a resource token." + '\n')
        params = urlparse.parse_qs(response.content)
        sys.stdout.write("Resource key: %s" % params['oauth_token'][0] + '\n')
        sys.stdout.write("Resource secret: %s" % params['oauth_token_secret'][0] + '\n')
    else:
        handle_error(response)
    sys.stdout.write('\n')


