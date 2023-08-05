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

#CodernityDB.index:


class IndexException(Exception):
    pass


class IndexNotFoundException(IndexException):
    pass


class ReindexException(IndexException):
    pass


class TryReindexException(ReindexException):
    pass


class ElemNotFound(IndexException):
    pass


class DocIdNotFound(ElemNotFound):
    pass


class IndexConflict(IndexException):
    pass


class IndexPreconditionsException(IndexException):
    pass


#CodernityDB.storage:
class StorageException(Exception):
    pass


#CodernityDB.tree_index:
class NodeCapacityException(IndexException):
    pass


#CodernityDB.database:
class DatabaseException(Exception):
    pass


class RecordNotFound(DatabaseException):
    pass


class RevConflict(DatabaseException):
    pass


class DatabaseClientException(Exception):
    pass


class PreconditionsException(DatabaseException):
    pass


class RecordDeleted(DatabaseException):
    pass


class DatabaseConflict(DatabaseException):
    pass


class DatabasePathException(DatabaseException):
    pass


class DatabaseIsNotOpened(PreconditionsException):
    pass
