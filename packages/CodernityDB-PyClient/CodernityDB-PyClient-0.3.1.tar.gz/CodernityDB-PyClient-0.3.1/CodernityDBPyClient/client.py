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

import sys
import imp


class CodernityDBImportFinder(object):
    """
    An import hook that performs lookups for CodernityDB modules. It makes a embeded imports to make with remote database.
    """
    replace_classes = ['Database', ]
    rename_classes = {'CodernityDB.database_thread_safe': {'Database': 'ThreadSafeDatabase'},
                      'CodernityDB.database_super_thread_safe': {'Database': 'SuperThreadSafeDatabase'},
                      'CodernityDB.database_gevent': {'Database': 'GeventDatabase'}}

    replace_modules = {'CodernityDB.database': ['CodernityDBPyClient.all_exceptions', 'CodernityDBPyClient.database'],
                       'CodernityDB.index': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.hash_index': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.tree_index': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.storage': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.database_gevent': ['CodernityDBPyClient.database'],
                       'CodernityDB.database_super_thread_safe': ['CodernityDBPyClient.database'],
                       'CodernityDB.database_thread_safe': ['CodernityDBPyClient.database'],
                       'CodernityDB.debug_stuff': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.env': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.lfu_cache_with_lock': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.lfu_cache': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.misc': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.patch': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.rr_cache_with_lock': ['CodernityDBPyClient.all_exceptions'],
                       'CodernityDB.rr_cache': ['CodernityDBPyClient.all_exceptions'],
                       }

    recur_set = set()

    def find_module(self, fullname, path=None):
        self.path = path
        self.main_replace_modules = [name.split(
            '.')[0] for name in self.replace_modules.keys()]
        if fullname == 'CodernityDB' and not fullname in self.recur_set:
            return self
        elif fullname in self.recur_set or not fullname.startswith(tuple(self.replace_modules)) or fullname.startswith('CodernityDBPyClient'):
            try:
                self.recur_set.remove(fullname)
            except:
                pass
            return None
        else:
            return self

    def load_module(self, fullname):
        self.recur_set.add(fullname)
        name_tab = fullname.split('.')
        if len(name_tab) > 2:
            name = name_tab[-1]
            if not name in sys.modules['.'.join(name_tab[:-1])].__dict__:
                raise ImportError('cannot import name %s' % name)
            return sys.modules['.'.join(name_tab[:-1])].__dict__[name]
        else:
            try:
                if len(name_tab) > 1:
                    imported_module = __import__(fullname, globals(), locals(
                    ), [], 0).__dict__[name_tab[-1]]
                else:
                    imported_module = __import__(fullname,
                                                 globals(), locals(), [], 0)
            except ImportError:
                is_imported = False
                if len(name_tab) == 1:
                    imported_module = sys.modules.setdefault(fullname,
                                                             imp.new_module(fullname))
                    imported_module.__file__ = fullname
                    imported_module.__name__ = fullname
                    imported_module.__path__ = []
                    imported_module.__loader__ = self
                    imported_module.__package__ = fullname
                elif fullname in self.replace_modules:
                    imported_module = __import__('.'.join(name_tab[:-1]))
                    new_module = sys.modules.setdefault(fullname,
                                                        imp.new_module(fullname))
                    new_module.__file__ = fullname
                    new_module.__name__ = fullname
                    new_module.__path__ = []
                    new_module.__loader__ = self
                    new_module.__package__ = fullname
                    imported_module.__dict__[name_tab[-1]] = new_module
                else:
                    raise
            else:
                is_imported = True

            if fullname in self.replace_modules:
                for replace_name in self.replace_modules[fullname]:
                    replaced_module = __import__(replace_name)
                    for key in sys.modules[replace_name].__dict__:
                        if (not key.startswith('__') or not key.endswith('__')) and (key in self.replace_classes or not is_imported):
                            if fullname in self.rename_classes and key in self.rename_classes[fullname]:
                                new_key = self.rename_classes[fullname][key]
                            else:
                                new_key = key
                            sys.modules[fullname].__dict__[new_key] = sys.modules[replace_name].__dict__[key]
        return imported_module


def setup():
    """
    Call this function **before** any of your CodernityDB imports to make use of import_hook and remote database.
    """
    sys.meta_path.append(CodernityDBImportFinder())
