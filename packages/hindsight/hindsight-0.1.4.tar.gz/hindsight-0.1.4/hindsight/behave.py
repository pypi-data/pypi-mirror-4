import urllib
import urllib2
import base64
from zipfile import ZipFile
from StringIO import StringIO

class JiraConnector:

    def fetch(self, host, key, username=None, password=None, dir='./', manual=1):
        if not host.endswith('/'):
            host += '/'

        path = host+'rest/cucumber/1.0/project/'+key+'/features?'+urllib.urlencode({'manual':bool(manual)})
        print 'Fetching from: ' + path

        req = urllib2.Request(path)
        req.add_header('Accept', 'application/zip')
        if username:
            base64string = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
            req.add_header("Authorization", "Basic %s" % base64string)

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            raise Exception('HTTPError (' + str(e.code) + '): ' + e.reason)
        except urllib2.URLError, e:
            raise Exception('URLError: ' + e.reason)
        else:
            print 'Fetched.'
            print 'Preparing to extract...'
            zip = ZipFile(StringIO(res.read()))
            infolist = zip.infolist()
            zip.extractall(path=dir)
            print 'Extracted ' + str(infolist.__len__()) + ' feature files into "' + dir + '"'