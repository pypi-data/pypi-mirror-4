import collections
import copy
import glob
import math
import os
import struct
import subprocess
import tempfile
import time
import httplib
import urllib
import urllib2
import socket
import json
import glob

import datetime
import dateutil
import dateutil.tz

import emdash.config
import emdash.log
import emdash.transport

# Helper functions

def ctime(filename):
    return os.stat(filename).st_ctime

def filetime(filename):
    # Try to get the file creation time
    ct = os.path.getctime(filename)
    t = datetime.datetime.fromtimestamp(ct).replace(tzinfo=emdash.config.tzlocal)
    return t.isoformat()

def walk(path, exclude=None, include=None, seen=None):
    if not path:
        return []
    if include is None:
        include = []
    if exclude is None:
         exclude = ['.json', 'EMAN2DB']
    if seen is None:
        seen = set()

    ret = set()

    if not path:
        return

    for root, sub, files in os.walk(path):
        # Note: filter out hidden directories and files.
        for i in filter(lambda x:x.startswith(".") or x in exclude, sub):
            sub.remove(i)

        for f in files:
            fn = os.path.join(root, f)
            _, ext = os.path.splitext(f)

            if fn in seen:
                continue
            seen.add(fn)

            if f.startswith("."):
                pass
            elif ext in exclude:
                pass
            elif not include:
                ret.add(fn)
            elif ext in include:
                ret.add(fn)

    return sorted(ret, key=ctime)



##### Base Transport #####

# Handler registration
def get_handler(handler):
    return Handler.get_handler(handler)
    

class Handler(object):
    
    # Default parameter
    param = 'file_binary'

    # Default record type
    rectype = 'folder' 

    # Allowed extensions
    exts = []     
    
    # Handler registration
    _handlers = {}
    _handlers_ext = {}

    def __init__(self, name='', data=None, *args, **kwargs):
        self.path = None
        self.seen = set()
        self.name = name
        self.data = data or {}
        self.wait = 0
        self.init(*args, **kwargs)
        
    def init(self, *args, **kwargs):
        pass

    def setwait(self, t):
        self.wait = t

    ##### Handler registration #####
    
    @classmethod
    def get_handler(cls, handler=None):
        if handler not in cls._handlers:
            # emdash.log.error("No such handler: %s"%handler)
            handler = None
        return cls._handlers.get(handler)()

    @classmethod
    def register_handler(cls, name=None):
        def inner(h):
            cls._handlers[name] = h
            for ext in getattr(h, 'exts', []):
                cls._handlers_ext[ext] = name
            return h
        return inner
    
    @classmethod
    def new(cls, *args, **kwargs):
        # Return a new instance of this class
        return cls(*args, **kwargs)


    ##### Utilty methods #####    
        
    def log(self, *args, **kwargs):
        kwargs['name'] = self.name
        emdash.log.msg(*args, **kwargs)

    def sidecar_read(self, filename):
        """Read the JSON sidecar."""
        try:
            return json.load(file(filename+".json","r")) or {}
        except:
            return {}

    def sidecar_write(self, filename, data):
        """Write the JSON sidecar."""
        data = data or {}
        try:
            json.dump(data, file(filename+".json", "w"), indent=True)
            # self.log("Wrote sidecar: %s.json"%filename)
        except:
            pass
            

    ##### HTTP Transfers #####

    def _upload(self, path, data=None, opener_cls=None):
        t = time.time()
        opener_cls = opener_cls or emdash.transport.PostHandler
        opener = opener_cls(log=self.log)
        resp = opener.open(path, data)
        status, reason, response = resp.status, resp.reason, resp.read()
        resp.close()

        if status not in range(200, 400):
            raise httplib.HTTPException, "Error: %s"%(reason)

        try:
            rec = json.loads(response)
        except Exception, e:
            emdash.log.error("Couldn't read JSON response: %s"%e, exception=e)
            rec = {}
        
        # kbsec = (filesize / (time.time() - t))/1024
        # self.log("Uploaded to record %s @ %0.2f KB/sec"%(rec.get("name"), kbsec))
        self.log("Upload completed in %5.2f s"%(time.time()-t))
        return rec

    def _upload_post(self, *args, **kwargs):
        kwargs['opener_cls'] = emdash.transport.PostHandler
        return self._upload(*args, **kwargs)
        
    def _upload_put(self, *args, **kwargs):
        kwargs['opener_cls'] = emdash.transport.PutHandler
        return self._upload(*args, **kwargs)

    def _download(self):
        pass

    def _retry(self, method, *args, **kwargs):
        pass



class FileHandler(Handler):

    ##### FileHandler Polling interface #####

    def poll(self):
        # Find suitable items in path, and return FileHandlers.
        #   These FileHandlers need to have an ID set (e.g. a filename)
        #   that will be used to communicate between threads.
        # The default implementation is to walk the
        #   filesystem, and return filenames that
        #   match a list of extensions.
        ret = []
        for filename in walk(self.path, seen=self.seen):
            item = self.check(filename)
            if item:
                ret.append(item)
        return ret

    def check(self, item):
        if not self.exts:
            return item
        _, ext = os.path.splitext(item)
        if ext in self.exts:
            return item

    def set_path(self, path):
        self.path = unicode(path)
        self.seen = set()

    def auto_enqueue(self):
        return True
    
    # Read metadata
    def _extract(self):
        return {}

    ##### Transport interface #####

    def display_name(self):
        """String to display in the upload queue."""
        return os.path.basename(self.name or 'filename')

    def display_filename(self):
        """(Optional) A filename that can be opened, e.g. to view in EMAN2"""
        return self.name or 'filename'

    def upload(self):
        self.log("\n--- Starting upload: %s ---"%self.name)
        self.log("Using handler:", self)
        self.log("Checking for previously uploaded files...")

        # Check JSON
        check = self.sidecar_read(self.name)
        if check.get('name'):
            self.log("File already exists in database -- check %s"%check.get('name'))
            return check

        # Wait a small amount of time before completing (default=0)
        if self.wait:
            self.log("Waiting %s seconds before proceeding"%self.wait)
            time.sleep(self.wait)

        # Data to upload
        fileobj = open(self.name, "rb")

        # This upload method will always create a new record for each file.
        target = self.data.get('_target')

        # New record request
        qs = {}
        qs['_format'] = 'json'
        qs['ctxid'] = emdash.config.get('ctxid')
        qs['date_occurred'] = filetime(self.name)
        for k,v in self.data.items():
            if not k.startswith('_'):
                qs[k] = v

        # File to upload
        qs[self.param] = fileobj

        # Extract metadata...
        qs.update(self._extract())
        
        # Try to upload.
        path = '/record/%s/new/%s/'%(target, self.rectype)
        # ... default is PUT -- much faster, less memory.
        rec = self._upload_put(path, qs)

        # Write out the sidecar file.
        self.sidecar_write(self.name, {"name":rec.get('name')})

        # Return the updated (or new) record..
        return rec

    def _check_db(self):
        # Check the DB is ready for this file
        pass

    def download(self):
        pass



@Handler.register_handler()
class AutoHandler(FileHandler):
        
    # This will try to find a handler based on file name..
    @classmethod
    def new(cls, name=None, data=None, *args, **kwargs):
        _, ext = os.path.splitext(unicode(name))

        # Ignore the default handler.
        exthandler = cls._handlers_ext.get(ext)
        if exthandler:
            handler = cls._handlers.get(exthandler, FileHandler)
            return handler(name=name, data=data, *args, **kwargs)
        else:
            emdash.log.error("No handler found for file %s, extension: %s"%(name, ext))





__version__ = "$Revision: 1.33 $".split(":")[1][:-1].strip()
