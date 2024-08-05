import sys
import boto.sts
import boto.s3
import requests
import getpass
import configparser
import base64
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from os.path import expanduser
from urllib.parse import urlparse, urlunparse, urljoin
from requests_ntlm import HttpNtlmAuth
import re
import argparse
import os
parser = argparse.ArgumentParser(description='Hello, You have reached a Program to generate temporary AWS Credentials...')
parser.add_argument("username", help="Prints the user name.")
parser.add_argument("password", help="Prints the password.")
parser.add_argument("rolearn", help="Prints the role arn.")
args = parser.parse_args()
print(args)
def store_aws_credentials():
    """
        Method to generate the temporary SAML tokens
    """
    credentials = []
    try:
        print("----------------------------------------")
        print("SAML TOKENS for accessing AWS Resources")
        print("-----------------------------------------")

        region = "us-east-1"
        duration = 3600
        print('')
        username = args.username
        password = args.password
        print('')
        requested_role_arn = args.rolearn
        acct_no = re.search('::(.+?):', requested_role_arn).group(1)
        requested_principal_arn = "arn:aws:iam::"+str(acct_no)+":saml-provider/PFE-AWS-PROD"
        sslverification = True
        idpentryurl = "http://awsprodv2.pfizer.com/"
        # output format: The AWS CLI output format that will be configured in the
        # saml profile (affects subsequent CLI calls)
        outputformat = 'json'
        # minimal redentials under the default profile
        awsconfigfile = '/.aws/credentials'
        home = expanduser("~")
        filename = home + awsconfigfile
        directory = home+'/.aws'
        if not os.path.exists(directory):
            os.makedirs(directory)
        if not os.path.exists(filename):
            open(filename, 'w').close()
            # Read in the existing config file
            config = configparser.RawConfigParser()
            config.add_section('default')
            config.set('default', 'output', outputformat)
            config.set('default', 'region', region)
            config.set('default', 'aws_access_key_id', "")
            config.set('default', 'aws_secret_access_key', "")
            # Write the updated config file
            with open(filename, 'w+') as minimalconfigfile:
                config.write(minimalconfigfile)
         # Initiate session handler
        session = requests.Session()
         # Programatically get the SAML assertion

        # Opens the initial AD FS URL and follows all of the HTTP302 redirects
        response_1 = session.get(idpentryurl, verify=sslverification)
        # fetch one more time to get the login form
        response_2 = session.get(response_1.url, verify=sslverification)

        # fill out and submit the login form
        soup_form = BeautifulSoup(response_2.text, features="html.parser")
        auth_form = soup_form.find_all('form')[0]
        action = auth_form.attrs.get("action")
        method = auth_form.attrs.get("method", "get")
        inputs = {}
        for input_tag in auth_form.find_all("input"):
            inputs[input_tag.attrs.get("name")] = input_tag.attrs.get("value")

        # add in the username/password to the form inputs
        inputs['pf.username'] = username
        inputs['pf.pass'] = password

        form_url = urljoin(response_2.url, action)

        # submit the form
        response_3 = session.post(form_url, data=inputs)

        # Decode the response and extract the SAML assertion
        soup = BeautifulSoup(response_3.text, features="html.parser")
        assertion = ''

        # Look for the SAMLResponse attribute of the input tag (determined by
        # analyzing the debug print lines above)
        for inputtag in soup.find_all('input'):
            if (inputtag.get('name') == 'SAMLResponse'):
                # print(inputtag.get('value'))
                assertion = inputtag.get('value')

        if (assertion == ''):
            # Insert valid error checking/handling
            print('Response did not contain a valid SAML assertion')

        #print("AWS ROLES for the user: %s " % awsroles)
        role_arn = requested_role_arn
        principal_arn = requested_principal_arn
        print("Your Role Arn:"+role_arn)
        print("Your Principal Arn:"+principal_arn)
        # Use the assertion to get an AWS STS token using Assume Role with SAML
        conn = boto.sts.connect_to_region(region)
        token = conn.assume_role_with_saml(role_arn, principal_arn, assertion, duration_seconds=duration)
        #print(token)
        # Write the AWS STS token into the AWS credential file

        # Read in the existing config file
        config = configparser.RawConfigParser()
        config.read(filename)

        # Put the credentials into the default credentials
        if not config.has_section('default'):
            config.add_section('default')

        config.set('default', 'output', outputformat)
        config.set('default', 'region', region)
        config.set('default', 'aws_access_key_id', token.credentials.access_key)
        config.set('default', 'aws_secret_access_key', token.credentials.secret_key)
        config.set('default', 'aws_session_token', token.credentials.session_token)

        # Write the updated config file
        with open(filename, 'w+') as configfile:
            config.write(configfile)
        print('Your new access key pair has been stored in the AWS configuration file {0} under the saml profile.'.format(filename))

    except Exception as e:
            print("ERROR : FAILED TO generate SAML tokens : %s " % e)

if __name__ == '__main__':
    #print("Hello, You have reached a Program to generate temporary AWS Credentials...")
    store_aws_credentials()
