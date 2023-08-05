#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2011-2012 Codernity (http://codernity.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# needed because of globals()[...]
from CodernityDB.database import DatabaseException, RecordNotFound, RevConflict, PreconditionsException, \
    RecordDeleted, DatabaseConflict, DatabasePathException, DatabaseIsNotOpened
from CodernityDB.index import IndexException, IndexNotFoundException, ReindexException, TryReindexException, ElemNotFound, DocIdNotFound, IndexConflict, IndexPreconditionsException
from CodernityDB.storage import StorageException
# ^^
import requests
import json
import sys
from inspect import getsource

try:
    import msgpack
except ImportError:
    has_msgpack = False
else:
    has_msgpack = True


try:
    from CodernityDB.index import Index
except ImportError:
    has_index = False
else:
    has_index = True


class Unauthorized(DatabaseException):
    pass


class DatabaseClientException(DatabaseException):
    pass

content_types = {
    'application/json': (lambda x, enc: json.loads(x, encoding=enc),
                         lambda x, enc: json.dumps(x, encoding=enc))
}
content_types['json'] = content_types['application/json']

if has_msgpack:
    content_types['application/msgpack'] = (lambda x, enc: msgpack.unpackb(x, encoding=enc),
                                            lambda x, enc: msgpack.packb(x, encoding=enc))
    content_types['msgpack'] = content_types['application/msgpack']


def remote_excepthook(type, value, traceback):
    _traceback = getattr(value, 'remote_traceback', traceback)
    if _traceback is None:
        _traceback = traceback
    # for some reason when _traceback it doesn't work at all (replaced by traceback)
    sys.__excepthook__(type, value, traceback)

sys.excepthook = remote_excepthook


def raise_proper_exception(response, load_fun):
    """
    Raises correct exception it will try to raise the same exception as on remote side
    """
    def get_exception_from_response(data):
        if not 'exception' in data or not 'reason' in data:
            raise DatabaseException('Invalid response')

        if data['exception'] in globals():
            exc = globals()[data['exception']]
        else:
            try:
                import exceptions
                exc = getattr(exceptions, data['exception'])
            except AttributeError:
                exc = Exception
        if 'traceback' in data:
            traceback = data['traceback']
        else:
            traceback = None
        return traceback, exc(data['reason'])

    if response.status_code == 401:
        response.raw.read()
        raise Unauthorized("Authorization failed")
    try:
        data = load_fun(response.raw.read())
    except:
        raise DatabaseException(response.raw.reason)
    else:
        traceback, exc = get_exception_from_response(data)
        if traceback is not None:
            exc.remote_traceback = traceback
        raise exc


class NONE:
    """
    For internal use only, different "none" than builtin None.
    """
    pass


class Database(object):
    """
    All methods are exactly like methods in CodernityDB embeded. So refer to that documentation for methods description

    :param string path: path to database (will work only when remote database is not opened yet)
    :param string url: a url to connect to remote database
    :param boolean keep_alive: keep alive for http or not
    :param tuple auth: an authorization data for remote database. an iterable of (login, password)
    :param string content_type: a default content type to use with database. by default ``application/json`` but change it to ``application/msgpack`` if you want use msgpack instead of json (which is recommended)
    :param string encoding: a data encoding
    :param boolean connect: connect to remote database automaticaly or not.

    """

    custom_header = ""

    def __init__(self, path=None, url='http://localhost:9876', keep_alive=True, auth=('admin', 'password'), content_type='application/json', encoding='utf-8', connect=True):
        self._path = path
        self.set_content_type(content_type)
        self.url = url
        self.path = path
        self.keep_alive = keep_alive
        self.auth = auth
        self.set_encoding(encoding)
        self.session = None
        if connect:
            self.connect()
            #self.initialize(path, makedir=False)

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, data):
        if self._path is None:
            self._path = data
        elif self._path == data:
            pass
        else:
            raise DatabaseClientException(
                "You can't change path when remote database is connected")

    def __dumps(self, data):
        fun = content_types[self.content_type][1]
        return fun(data, self.encoding)

    def __loads(self, data):
        fun = content_types[self.content_type][0]
        return fun(data, self.encoding)

    def remote_init(self):
        if self.opened():
            details = self.get_db_details()
            self.path = details['path']
        else:
            if self.path:
                self.initialize(self.path, makedir=False)

    def check_connection(self):
        try:
            self.get_version()
        except:
            self.disconnect()
            raise DatabaseClientException("Database not found")
        else:
            return True

    def _request(self, function, data={}):
        if not self.session:
            raise DatabaseClientException("Not connected")
        headers = {
            'Content-Type': self.content_type,
            'Content-Encoding': self.encoding
        }
        url = "%s/%s" % (self.url, function)
        data = self.__dumps(data)
        result = self.session.post(url, headers=headers,
                                   auth=self.auth, data=data, prefetch=False)
        if not result.status_code == requests.codes.ok:
            raise_proper_exception(result, self.__loads)
        return result.raw.read()

    def set_auth(self, login, password):
        self.auth = (login, password)

    def set_content_type(self, content_type):
        if content_type in content_types.keys():
            self.content_type = content_type
        else:
            raise DatabaseClientException(
                'Use one of these: %s' % (content_types.keys()))

    def set_encoding(self, encoding):
        self.encoding = encoding

    def connect(self):
        self.session = requests.session()
        self.session.config['keep_alive'] = self.keep_alive
        res = self.check_connection()
        if res:
            self.remote_init()

    def disconnect(self):
        self.session = None
        self._path = None

    def header_for_indexes(self, index_name, index_class, db_custom="", ind_custom="", classes_code=""):
        function = 'get_index_header'
        result = self._request(function)
        header = self.__loads(result)
        header = header.replace("__REPLACE_NAME__", index_name)
        header = header.replace("__REPLACE_CLASS__", index_class)
        header = header.replace("# db_custom\n", "# db_custom\n%s" % db_custom)
        header = header.replace(
            "# ind_custom\n", "# ind_custom\n%s" % ind_custom)
        header = header.replace(
            "# classes_code\n", "# classes_code\n%s" % classes_code)
        return header

    def opened(self):
        function = 'opened'
        result = self._request(function)
        return self.__loads(result)

    def open(self, path=None):
        if self.opened():
            return self.path
        function = 'open'
        req_data = {}
        if path:
            self.path = path
            req_data = {'path': self.path}
        result = self._request(function, req_data)
        return self.__loads(result)

    def close(self):
        function = 'close'
        result = self._request(function)
        return self.__loads(result)

    def exists(self):
        function = 'exists'
        result = self._request(function)
        return self.__loads(result)

    def destroy(self):
        function = 'destroy'
        result = self._request(function)
        return self.__loads(result)

    def initialize(self, path=None, makedir=True):
        function = 'initialize'
        if path:
            self.path = path
        req_data = {'path': self.path, 'makedir': makedir}
        result = self._request(function, req_data)
        return self.__loads(result)

    def __get_new_index_code(self, new_index, ind_kwargs):
        if isinstance(new_index, basestring) and not new_index.startswith("path:"):
            new_index_code = new_index
            name = new_index.splitlines()[0][2:]
            name = name.strip()
        elif isinstance(new_index, basestring) and new_index.startswith("path:"):
            raise DatabaseClientException("Not supported on client side")
        elif has_index and isinstance(new_index, Index):
            name = new_index.name
            code = getsource(new_index.__class__)
            cls_code = getattr(new_index, 'classes_code', [])
            classes_code = ""
            for curr in cls_code:
                classes_code += getsource(curr) + '\n\n'
            header = self.header_for_indexes(name,
                                             new_index.__class__.__name__,
                                             getattr(
                                                 self, 'custom_header', ''),
                                             getattr(new_index,
                                                     'custom_header', ''),
                                             classes_code)
            new_index_code = header + code
            init_arguments = new_index.__class__.__init__.im_func.func_code.co_varnames[3:]  # ignore self, path and name
            for curr in init_arguments:
                if curr not in ('args', 'kwargs'):
                    v = getattr(new_index, curr, NONE())
                    if not isinstance(v, NONE):
                        ind_kwargs[curr] = v
        else:
            raise PreconditionsException("Argument must be Index instance or valid string index format")
        return new_index_code

    def add_index(self, new_index, create=True, ind_kwargs=None):
        if ind_kwargs is None:
            ind_kwargs = {}
        function = 'add_index'
        new_index_code = self.__get_new_index_code(new_index, ind_kwargs)
        data = {"new_index": new_index_code,
                "create": create,
                "ind_kwargs": ind_kwargs}
        result = self._request(function, data)
        return self.__loads(result)

    def edit_index(self, index, reindex=False, ind_kwargs=None):
        if ind_kwargs is None:
            ind_kwargs = {}
        function = 'edit_index'
        new_index_code = self.__get_new_index_code(index, ind_kwargs)
        data = {"index": new_index_code,
                "reindex": reindex,
                "ind_kwargs": ind_kwargs}
        result = self._request(function, data)
        return self.__loads(result)

    def get_version(self):
        function = 'get_version'
        data = {}
        result = self._request(function, data)
        return self.__loads(result)

    def get_index_code(self, index_name):
        function = 'get_index_code'
        data = {'index_name': index_name}
        result = self._request(function, data)
        return self.__loads(result)

    def get_indexes_names(self):
        function = 'get_indexes_names'
        result = self._request(function)
        return self.__loads(result)

    def destroy_index(self, index):
        function = 'destroy_index'
        if has_index and isinstance(index, Index):
            raise DatabaseClientException("Not supported on client side")
        if index == 'id':
            raise PreconditionsException("Id index cannot be destroyed")
        data = {'index': index}
        self._request(function, data)

    def compact_index(self, index):
        function = 'compact_index'
        if has_index and isinstance(index, Index):
            index = index.name
        data = {'index': index}
        self._request(function, data)
        return None

    def compact_indexes(self):
        indexes = self.get_indexes_names()
        for index in indexes:
            self.compact_index(index)

    def reindex_index(self, index):
        function = 'reindex_index'
        if has_index and isinstance(index, Index):
            raise DatabaseClientException("Not supported on client side")
#            index = index.name
        if index == 'id':
            raise PreconditionsException("Id index cannot be reindexed")
        data = {'index': index}
        self._request(function, data)

    def reindex_indexes(self):
        function = 'reindex'
        self._request(function)

    def reindex(self):
        self.reindex_indexes()

    def insert(self, data):
        function = 'insert'
        if '_rev' in data:
            raise PreconditionsException(
                "Can't add record with forbidden fields")
        req_data = {'data': data}
        result = self._request(function, req_data)
        data_info = self.__loads(result)
        data.update(data_info)
        return data_info

    def update(self, data):
        function = 'update'
        if not '_rev' in data or not '_id' in data:
            raise PreconditionsException("Can't update without _rev or _id")
        req_data = {'data': data}
        result = self._request(function, req_data)
        data_info = self.__loads(result)
        data.update(data_info)
        return data_info

    def get(self, index_name, key, with_doc=False, with_storage=True):
        function = 'get'
        data = {'index_name': index_name,
                'key': key,
                'with_doc': with_doc,
                'with_storage': with_storage
                }
        result = self._request(function, data)
        return self.__loads(result)

    def get_many(self, index_name, key=None, limit=1, offset=0, with_doc=False, with_storage=True, **kwargs):
        function = 'get_many'
        if index_name == 'id':
            raise PreconditionsException("Can't get many from `id`")
        data = {'index_name': index_name,
                'key': key,
                'limit': limit,
                'offset': offset,
                'with_doc': with_doc,
                'with_storage': with_storage
                }
        data.update(kwargs)
        result = self._request(function, data)
        return self.__loads(result)

    def all(self, index_name, limit=-1, offset=0, with_doc=False, with_storage=True):
        function = 'all'
        data = {'index_name': index_name,
                'limit': limit,
                'offset': offset,
                'with_doc': with_doc,
                'with_storage': with_storage
                }
        result = self._request(function, data)
        return self.__loads(result)

    def delete(self, data):
        function = 'delete'
        req_data = {'data': data}
        self._request(function, req_data)
        return True

    def compact(self):
        function = 'compact'
        self._request(function)

    def flush(self):
        function = 'flush'
        self._request(function)

    def fsync(self):
        function = 'fsync'
        self._request(function)

    def get_index_details(self, name):
        function = 'get_index_details'
        req_data = {'name': name}
        result = self._request(function, req_data)
        return self.__loads(result)

    def get_db_details(self):
        function = 'get_db_details'
        result = self._request(function)
        return self.__loads(result)

    def count(self, target_funct, *args, **kwargs):
        if callable(target_funct):
            target_funct = target_funct.__name__
        function = 'count/%s' % target_funct
        if args:
            function += '/' + '/'.join(map(self.__dumps, args))
        req_data = kwargs
        result = self._request(function, req_data)
        return self.__loads(result)

    def run(self, target_index, target_funct, *args, **kwargs):
        if callable(target_funct):
            target_funct = target_funct.__name__
        function = 'run/%s' % target_index
        args = (target_funct, ) + args
        function += '/' + '/'.join(map(self.__dumps, args))
        req_data = kwargs
        result = self._request(function, req_data)
        return self.__loads(result)

    def create(self, path=None, **kwargs):
        function = 'create'
        req_data = kwargs
        if path:
            self.path = path
            req_data['path'] = path
        result = self._request(function, req_data)
        return self.__loads(result)

    def set_indexes(self, indexes=[]):
        for index in indexes:
            self.add_index(index, create=False)

####################################################################
#
#                        Not supported
#
####################################################################

    def single_update_index(self):
        raise DatabaseClientException("Not supported on client side")

    def update_id_index(self, data):
        raise DatabaseClientException("Not supported on client side")

    def update_indexes(self, data):
        raise DatabaseClientException("Not supported on client side")

    def single_insert_index(self, index, data, doc_id):
        raise DatabaseClientException("Not supported on client side")

    def insert_id_index(self, data):
        raise DatabaseClientException("Not supported on client side")

    def insert_indexes(self, data):
        raise DatabaseClientException("Not supported on client side")

    def single_delete_index(self, index, data, doc_id, old_data):
        raise DatabaseClientException("Not supported on client side")

    def delete_id_index(self, data):
        raise DatabaseClientException("Not supported on client side")

    def delete_indexes(self, data):
        raise DatabaseClientException("Not supported on client side")

    def single_reindex_index(self, index, data):
        raise DatabaseClientException("Not supported on client side")

    def _add_single_index(self, p, i, index):
        raise DatabaseClientException("Not supported on client side")

    def _read_index_single(self, p, ind):
        raise DatabaseClientException("Not supported on client side")

    def _read_indexes(self):
        raise DatabaseClientException("Not supported on client side")
