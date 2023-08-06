import json
import httplib
from threading import Lock

import bottle


import scan


MAX_POST_SIZE = 2**20 * 100 # 100 MB
class ScannerServer(object):
    def __init__(self, max_post_size=MAX_POST_SIZE, **scanner_kwargs):
        self._max_post_size = max_post_size 
        self.scanner = scan.SyncScanner(**scanner_kwargs)

    @bottle.post("scan")
    def scan(self):
        filenames = []
        data = []
        bytes_remaining = self._max_post_size
        for filename, field in request.files.iteritems():
            if bytes_remaining <= 0:
                bottle.abbort(httplib.REQUEST_ENTITY_TOO_LARGE, 
                        'POST was > %s bytes' % MAX_POST_SIZE)
            d = field.file.read(bytes_remaining)
            bytes_remaining -= len(data)
            filenames.append(filename)
            data.append(d)

        try:
            res = self.scanner.match_data(data)
            results = zip(filenames, res)
        except:
            bottle.abort(httplib.INTERNAL_SERVER_ERROR, traceback.format_exc())

        return results 
    

