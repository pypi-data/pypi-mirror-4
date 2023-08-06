import requests
from zipfile import ZipFile
from StringIO import StringIO

class JiraConnector:

    def fetch(self, host, key, username=None, password=None, dir='./', manual=1, verify=0):
        if not host.endswith('/'):
            host += '/'
        path = host+'rest/cucumber/1.0/project/'+key+'/features'
        headers = {'accept':'application/zip'}
        payload = {'manual':bool(manual)}

        print 'Fetching from: ' + path
        req = requests.get(path, auth=(username, password), headers=headers, params=payload, verify=bool(verify))
        if req.status_code == 200:
            print 'Fetched.'
            print 'Preparing to extract...'
            zip = ZipFile(StringIO(req.content))
            infolist = zip.infolist()
            zip.extractall(path=dir)
            print 'Extracted ' + str(infolist.__len__()) + ' feature files into "' + dir + '"'
        else:
            req.raise_for_status()
