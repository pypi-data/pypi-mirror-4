import argparse
import requests
from hindsight.behave import JiraConnector

def main():
    parser = argparse.ArgumentParser(description='Wrapper for BehaveForJira class to download features from the command line')
    parser.add_argument('host', help='Host URI for Jira installation')
    parser.add_argument('key', help='Project key to download features from')
    parser.add_argument('-u', '--username', help='User with Behave rights on project')
    parser.add_argument('-p', '--password', help='Password for User')
    parser.add_argument('-d', '--directory', help='Directory to download features to (default ./)')
    parser.add_argument('-m', '--manual', help='Include manual tagged scenarios in download', action='store_true')
    parser.add_argument('--verify', help='Enable SSL verification for CA certificates', action='store_true')
    args = parser.parse_args()

    if not args.directory:
        dir = './'
    else:
        dir = args.directory

    if not args.username:
        username = None
        password = None
    else:
        username = args.username
        if not args.password:
            password = None
        else:
            password = args.password

    conn = JiraConnector()
    try:
        conn.fetch(host=args.host,key=args.key,username=username,password=password,manual=args.manual,dir=dir,verify=args.verify)
    except (requests.HTTPError, requests.ConnectionError, requests.RequestException) as e:
        print str(e)