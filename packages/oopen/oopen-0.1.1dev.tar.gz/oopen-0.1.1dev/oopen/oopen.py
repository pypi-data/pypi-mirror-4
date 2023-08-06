#!/usr/bin/env python

from cached_property import cached_property
import os
import hashlib
from datetime import datetime
from __builtin__ import file

__all__ = ['OOpen']

class OOpen(file):
    '''Object-Oriented file and path handling.'''

    def __init__(self, path, mode='r+'):
        self.path = os.path.abspath(path)
        self._mode = mode
        file.__init__(self, path, mode)
        self.is_modified = False

    def __move(self, value):
        "move the file, repopen file handle"
        #todo: Check if dir exists, & we have rights
        pos = self.tell()
        self.close()
        new = os.path.abspath(value)
        os.rename(self.abspath, new)
        self.path = new
        file.__init__(self, self.path, self._mode)
        self.seek(pos)
        self.is_modified = True

    def write(self, str_):

        self.is_modified = True
        return file.write(self, str_)
    write.__doc__ = "Triggers modified flag\n" + file.write.__doc__

    def writelines(self, sequence):
        self.is_modified = True
        return file.writelines(self, sequence)
    writelines.__doc__ = "Triggers modified flag\n" + file.writelines.__doc__

    @property
    def size(self):
        'filesize in bytes'
        return int(self.my_stat['st_size'])

    @property
    def kb(self):
        'filesize in kilobytes. In IEC units. 1 kb = 2^10 bytes'
        return self.size >> 10

    @property
    def mb(self):
        'filesize in megabytes . In IEC units. 1 mb = 2^20 bytes'
        return self.kb >> 10

    @property
    def gb(self):
        'filesize in gigabytes. In IEC units. 1 gb = 2^30 bytes'
        return self.mb >> 10

    @property
    def tb(self):
        'filesize in terabytes. In IEC units. 1 tb = 2^40 bytes'
        return self.gb >> 10

    @property
    def pb(self):
        'filesize in petabytes. In IEC units. 1 pb = 2^50 bytes'
        return self.tb >> 10

    @property
    def datetimes(self):
        'Return a tuple of datetimes (accessed, modified, created)'
        return (self.accessed_time, self.modified_time, self.created_time)

    @cached_property(ttl=1)
    def my_stat(self):
        'os.stat in dictionary form; this is cached with 1 second ttl'
        return self.my_stat_immediate

    @property
    def my_stat_immediate(self):
        'os.stat in dictionary form'
        os_stat = {}
        os_stat["st_mode"], os_stat["st_ino"], os_stat["st_dev"], os_stat["st_nlink"], \
            os_stat["st_uid"], os_stat["st_gid"], os_stat["st_size"], os_stat["st_atime"], \
            os_stat["st_mtime"], os_stat["st_ctime"] = os.stat(self.name)
        return os_stat

    def __get_hash(self, hash_type):
        if hash_type not in hashlib.algorithms:
            raise NotImplemented

        orig_position = self.tell()
        self.seek(0)
        hash_method = eval('hashlib.{}()'.format(hash_type))
        while True:
            data = self.read(4096)
            if len(data) == 0:
                break
            hash_method.update(data)

        self.seek(orig_position)
        return hash_method.hexdigest()

    @property
    def md5(self):
        'md5 hexdigest'
        return self.__get_hash('md5')

    @property
    def sha1(self):
        'sha1 hexdigest'
        return self.__get_hash('sha1')

    @property
    def sha224(self):
        'sha224 hexdigest'
        return self.__get_hash('sha224')

    @property
    def sha256(self):
        'sha256 hexdigest'
        return self.__get_hash('sha256')

    @property
    def sha384(self):
        'sha384 hexdigest'
        return self.__get_hash('sha384')

    @property
    def sha512(self):
        'sha512 hexdigest'
        return self.__get_hash('sha512')

    def __chown(chown_type):

        allowed = ['st_uid', 'st_gid']
        if chown_type not in allowed:
            raise ValueError

        def fget(self):
            return self.my_stat[chown_type]

        def fset(self, value):
            uid = value if chown_type == 'st_uid' else -1
            gid = value if chown_type == 'st_gid' else -1

            os.fchown(self, uid, gid)

        return {'fget': fget, 'fset': fset}

    owner = property(doc="(R/W) The file owner (as UID)", **__chown('st_uid'))
    group = property(doc="(R/W) The file group (as GID)", **__chown('st_gid'))

    def accessed_time():
        doc = "(R/W) The accessed time as a datetime object."

        def fget(self):
            return datetime.utcfromtimestamp(self.my_stat["st_atime"])

        def fset(self, value):
            value_epoch = (value - datetime.datetime(1970, 1, 1)).total_seconds()  # 1/1/1970 is the unix epoch
            os.utime(self.path, (value_epoch, self.my_stat_immediate['st_mtime']))

        def fdel(self):
            return False
        return locals()
    accessed_time = property(**accessed_time())

    def modified_time():
        doc = "(R/W) The modified time as a datetime object."

        def fget(self):
            return datetime.utcfromtimestamp(self.my_stat["st_mtime"])

        def fset(self, value):
            value_epoch = (value - datetime.datetime(1970, 1, 1)).total_seconds()  # 1/1/1970 is the unix epoch
            os.utime(self.path, (self.my_stat_immediate['st_atime'], value_epoch))

        def fdel(self):
            return False
        return locals()
    modified_time = property(**modified_time())

    @property
    def created_time(self):
        '(R) The created time as a datetime object. Note: the value returned is platform-dependendant.'
        return datetime.utcfromtimestamp(self.my_stat['st_ctime'])

    def position():
        doc = "(R/W) The position of the HEAD, like f.tell() and f.seek() combined."

        def fget(self):
            return self.tell()

        def fset(self, value):
            self.seek(value)
        return locals()
    position = property(**position())

    def abspath():
        doc = "(R/W) The absolute path of the file, including the filename."

        def fget(self):
            return os.path.abspath(self.path)

        def fset(self, value):
            if os.path.exists(value):
                raise OSError
            os.rename(fget(self), os.path.abspath(value))
            self.path = os.path.abspath(value)

        return locals()
    abspath = property(**abspath())

    def location():
        doc = "(R/W) The folder the file is in."

        def fget(self):
            return os.path.dirname(self.abspath)

        def fset(self, value):
            os.rename(os.path.join(fget(self), self.name),
                      os.path.join(value, self.name))
            self.path = os.path.abspath(os.path.join(value, self.name))

        return locals()
    location = property(**location())

    def name():
        doc = "(R/W) The name of the file."

        def fget(self):
            return os.path.basename(self.abspath)

        def fset(self, value):
            os.rename(self.abspath,
                      os.path.join(self.location, value))
            self.path = os.path.abspath(os.path.join(self.location, value))

        return locals()
    name = property(**name())

    def delete(self):
        pass

    def protect(self):
        pass

    def release(self):
        pass

    def copy(self):
        pass

    def touch(self):
        pass


