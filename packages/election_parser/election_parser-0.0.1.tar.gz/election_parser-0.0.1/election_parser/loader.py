import pycurl
import StringIO
import election_parser.utils
import gflags
import os

FLAGS = gflags.FLAGS

gflags.DEFINE_string('url', 
                      'http://media.sos.ca.gov/media/X12PG.zip',
                      'URL for CA\'s XML election data')

class BareLoader:
    @staticmethod
    def fetch(url=FLAGS.url):
        payload = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, payload.write)
        c.perform()
        c.close()
        return payload

    def read_data(self, data):
        return data.read()

class PostLoader:
    @staticmethod
    def fetch(url=FLAGS.url):
        payload = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, payload.write)
        c.perform()
        c.close()
        return payload

    def read_data(self, data):
        return data.read()

class ZipLoader:
    @staticmethod
    def fetch(url=FLAGS.url):
        payload = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, payload.write)
        c.perform()
        c.close()
        return election_parser.utils.ZipDict(payload), payload, os.path.basename(url)
    
    def read_data(self, data):
        # We assume there is only one data file, this may not be true
        # for other states, or even for CA - there are multiple files
        # provided by the state and its not certain quite yet that we
        # don't need both of them.
        for filename in data:
            if self.is_correct_file(filename):
                return data[filename].read()
