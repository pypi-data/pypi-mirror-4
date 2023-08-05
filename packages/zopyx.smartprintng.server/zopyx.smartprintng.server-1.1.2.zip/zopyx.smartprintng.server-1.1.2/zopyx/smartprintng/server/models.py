##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import threading
import base64
import glob
import os
import shutil
import tempfile
from stat import ST_CTIME
import shutil
from datetime import datetime
import time
import uuid
import zipfile
from logger import LOG
import mail_util
from zopyx.convert2.convert import Converter


class Server(object):
    """ SmartPrintNG Server Core Implementation """

    def __init__(self):
        self.num_requests = 0
        self.start_time = datetime.now()
        self.delivery_max_age = 1800   # deliver files only younger than xx seconds
        self.cleanup_after = 3600
        self.cleanup_last = time.time()
        self.keep_files_for = 3600     # keep files for no longer than xx seconds
        self._lock = threading.Lock()
        self.temp_directory = os.path.join(tempfile.gettempdir(), 
                                           'zopyx.smartprintng.server')
        if not os.path.exists(self.temp_directory):
            os.makedirs(self.temp_directory)

        self.spool_directory = os.path.join(tempfile.gettempdir(), 
                                           'zopyx.smartprintng.server-spool')
        if not os.path.exists(self.spool_directory):
            os.makedirs(self.spool_directory)

    def countRequest(self):
        self._lock.acquire()
        self.num_requests += 1
        self._lock.release()

    @property
    def start_time_as_str(self):
        return self.start_time.strftime('%d.%m.%Y %H:%M:%S')

    def _cleanup(self):
        """ Remove old and outdated files from the temporary and
            spool directory.
        """

        if time.time() - self.cleanup_last > self.cleanup_after:
            self._lock.acquire()
            try:
                self.__cleanup()
                self.cleanup_last = time.time()
            except Exception, e:
                LOG.error(e, exc_info=True)
            finally:
                self._lock.release()

    def __cleanup(self):
        for dir in os.listdir(self.temp_directory):
            destdir = os.path.join(self.temp_directory, dir)
            age = time.time() - os.stat(destdir)[ST_CTIME]
            if age > self.keep_files_for:
                shutil.rmtree(destdir)

        for name in os.listdir(self.spool_directory):
            fullname = os.path.join(self.spool_directory, name)
            age = time.time() - os.stat(fullname)[ST_CTIME]
            if age > self.keep_files_for:
                if os.path.exists(fullname):
                    shutil.rmtree(fullname)

    def _inject_base_tag(self, html_filename):
        """ All input HTML files contain relative urls (relative
            to the path of the main HTML file (the "working dir").
            So we must inject a BASE tag in order to call the external
            converters properly with the full path of the html input file
            since we do not want to change the process working dir (not
            acceptable in a multi-threaded environment).
            ATT: this should perhaps handled within zopyx.convert2
        """
        html = file(html_filename).read()
        pos = html.lower().find('<head>')
        if pos == -1:
            raise RuntimeError('HTML does not contain a HEAD tag')
        html = html[:pos] + '<head><base href="%s"/>' % html_filename + html[pos+6:]
        file(html_filename, 'wb').write(html)

    def _convert(self, html_filename, converter_name='pdf-prince'):
        """ Process a single HTML file """
        self._cleanup()
        return Converter(html_filename)(converter_name)

    def _processZIP(self, zip_archive, converter_name):

        LOG.info('Incoming request (%s, %d bytes)' % (converter_name, len(zip_archive)))
        ts = time.time()

        # temp directory handling 
        now = datetime.now().strftime('%Y%m%d%Z%H%M%S')
        ident = '%s-%s' % (now, uuid.uuid4())
        tempdir = os.path.join(self.temp_directory, ident)
        os.makedirs(tempdir)

        # store zip archive first
        zip_temp = os.path.join(tempdir, 'input.zip')
        file(zip_temp, 'wb').write(base64.decodestring(zip_archive))
        ZF = zipfile.ZipFile(zip_temp, 'r')
        for name in ZF.namelist():
            destfile = os.path.join(tempdir, name)
            if not os.path.exists(os.path.dirname(destfile)):
                os.makedirs(os.path.dirname(destfile))
            file(destfile, 'wb').write(ZF.read(name))
        ZF.close()

        # find HTML file
        html_files = glob.glob(os.path.join(tempdir, '*.htm*'))
        if not html_files:
            raise IOError('Archive does not contain any html files')
        if len(html_files) > 1:
            raise RuntimeError('Archive contains more than one html file')
        html_filename = html_files[0]
        # inject BASE tag containing the full local path (required by PrinceXML)
        self._inject_base_tag(html_filename)
        result = self._convert(html_filename, 
                               converter_name=converter_name)
        output_filename = result['output_filename']
        basename, ext = os.path.splitext(os.path.basename(output_filename))

        # Generate result ZIP archive with base64-encoded result
        zip_out = os.path.join(tempdir, '%s.zip' % ident)
        ZF = zipfile.ZipFile(zip_out, 'w')
        ZF.writestr('output%s' % ext, file(output_filename, 'rb').read())
        ZF.writestr('conversion-output.txt', result['output'])
        ZF.close()

        LOG.info('Request end (%3.2lf seconds)' % (time.time() - ts))
        return zip_out, output_filename

    def convertZIP(self, zip_archive, converter_name='pdf-prince'):
        """ Process html-file + images within a ZIP archive """

        self.countRequest()
        zip_out, output_filename = self._processZIP(zip_archive, converter_name)
        encoded_result = base64.encodestring(file(zip_out, 'rb').read())
        shutil.rmtree(os.path.dirname(zip_out))
        return encoded_result

    def convertZIPEmail(self, zip_archive, converter_name='pdf-prince', sender=None, recipient=None, subject=None, body=None):
        """ Process zip archive and send conversion result as mail """

        self.countRequest()

        zip_out, output_filename = self._processZIP(zip_archive, converter_name)
        mail_util.send_email(sender, recipient, subject, body, [output_filename])
        shutil.rmtree(os.path.dirname(zip_out))
        return True

    def availableConverters(self):
        """ Return a list of available converter names """
        from zopyx.convert2.registry import availableConverters
        self.countRequest()
        return availableConverters()

root = Server()

def get_root(environ):
    return root

if __name__ == '__main__':
    s = Server()
    print s.availableConverters() 

