import sys
import urllib
import urllib2
import base64
from zipfile import ZipFile

class JiraConnector:

    def fetch(self, host, key, username=None, password=None, dir='./', manual=1):
        if not host.endswith('/'):
            host += '/'

        path = host+'rest/cucumber/1.0/project/'+key+'/features?'+urllib.urlencode({'manual':bool(manual)})
        print 'Fetching from: ' + path

        req = urllib2.Request(path)
        req.add_header('Accept', 'application/zip')
        if username:
            prep = '%s:%s' % (username, password)
            base64string = base64.standard_b64encode(prep.encode('ascii'))
            encoded = 'Basic %s' % base64string.decode('ascii')
            req.add_header('Authorization', encoded)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            raise Exception('HTTPError (' + str(e.code) + '): ' + e.reason)
        except urllib2.URLError, e:
            raise Exception('URLError: ' + e.reason)
        else:
            print 'Fetched.'
            print 'Preparing to extract...'
            if sys.version[0] < '3':
                from StringIO import StringIO
                zip = ZipFile(StringIO(res.read()))
            else:
                from io import BytesIO
                zip = ZipFile(BytesIO(res.read()))
            infolist = zip.infolist()
            zip.extractall(path=dir)
            print 'Extracted ' + str(infolist.__len__()) + ' feature files into "' + dir + '"'


