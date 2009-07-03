# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Itaapy, ArsAperta, Pierlis, Talend

# Import from the Standard Library
from datetime import datetime
from cStringIO import StringIO
from os import listdir
from urlparse import urlsplit

# Import from gio
from gio import File, Error, content_type_get_mime_type
from gio import FILE_ATTRIBUTE_TIME_CHANGED, FILE_ATTRIBUTE_TIME_MODIFIED
from gio import FILE_ATTRIBUTE_TIME_ACCESS
from gio import FILE_ATTRIBUTE_STANDARD_SIZE, FILE_ATTRIBUTE_STANDARD_NAME
from gio import FILE_ATTRIBUTE_STANDARD_TYPE
from gio import FILE_TYPE_DIRECTORY, FILE_TYPE_REGULAR
from gio import FILE_TYPE_SYMBOLIC_LINK
from gio import FILE_ATTRIBUTE_ACCESS_CAN_READ
from gio import FILE_ATTRIBUTE_ACCESS_CAN_WRITE
from gio import FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE



######################################################################
# Constants
######################################################################
READ = 'r'
WRITE = 'w'
READ_WRITE = 'rw'
APPEND = 'a'



######################################################################
# Private API
######################################################################
def _is_file(g_file):
    try:
        info = g_file.query_info(FILE_ATTRIBUTE_STANDARD_TYPE)
        the_type = info.get_attribute_uint32(FILE_ATTRIBUTE_STANDARD_TYPE)
    except Error:
        return False
    return (the_type == FILE_TYPE_REGULAR or
            the_type == FILE_TYPE_SYMBOLIC_LINK)



def _is_folder(g_file):
    try:
        info = g_file.query_info(FILE_ATTRIBUTE_STANDARD_TYPE)
        the_type = info.get_attribute_uint32(FILE_ATTRIBUTE_STANDARD_TYPE)
    except Error:
        return False
    return the_type == FILE_TYPE_DIRECTORY



def _get_names(g_file):
    # Local ?
    if g_file.is_native():
        path = g_file.get_path()
        return listdir(path)

    children = g_file.enumerate_children(FILE_ATTRIBUTE_STANDARD_NAME)
    return [child.get_name() for child in children]



def _make_directory_with_parents(g_file):
    # Make the todo list
    todo = []
    while not g_file.query_exists():
        todo.append(g_file.get_basename())
        g_file = g_file.get_parent()

    # Make the directories
    while todo:
        g_file = g_file.resolve_relative_path(todo.pop())
        g_file.make_directory()



def _remove(g_file):
    # Is a directory ?
    if _is_folder(g_file):
        for child in _get_names(g_file):
            child = g_file.resolve_relative_path(child)
            _remove(child)
    g_file.delete()



def _copy(source, target):
    # "source to target/" or "source to target" ?
    if target.query_exists() and _is_folder(target):
        source_name = source.get_basename()
        target = target.resolve_relative_path(source_name)

    # Is a directory ?
    if _is_folder(source):
        # Copy the directory
        # XXX Must we handle the attributes ?
        target.make_directory()
        for child in _get_names(source):
            child_source = source.resolve_relative_path(child)
            child_target = target.resolve_relative_path(child)
            _copy(child_source, child_target)
    else:
        source.copy(target)



def _traverse(g_file):
    yield g_file.get_uri()

    # Is a directory ?
    if _is_folder(g_file):
        for child in _get_names(g_file):
            child = g_file.resolve_relative_path(child)
            for grandchild in _traverse(child):
                yield grandchild



######################################################################
# Public API
######################################################################
class Folder(object):

    def __init__(self, obj=None):
        if obj is None:
            self._folder = None
        elif type(obj) is str:
            self._folder = File(obj)
        elif isinstance(obj, File):
            self._folder = obj
        else:
            raise ValueError, 'unexpected obj "%s"' % obj


    ############################
    # Private API
    ############################
    def _get_g_file(self, uri):
        if type(uri) is not str:
            raise TypeError, 'unexpected "%s"' % repr(uri)

        # Your folder is None => new File
        if self._folder is None:
            return File(uri)

        # Your folder is not None, we must resolve the uri
        scheme, authority, path, query, fragment = urlsplit(uri)

        # A scheme or an authority => new File
        # XXX This is not truly exact:
        #     we can have a scheme and a relative path.
        if scheme or authority:
            return File(uri)

        # Else we resolve the path
        return self._folder.resolve_relative_path(uri)


    def _get_xtime(self, uri, attribut):
        g_file = self._get_g_file(uri)
        info = g_file.query_info(attribut)
        uint64 = info.get_attribute_uint64(attribut)
        return datetime.fromtimestamp(uint64)


    def _can_x(self, uri, attribut):
        g_file = self._get_g_file(uri)
        info = g_file.query_info(attribut)
        return info.get_attribute_boolean(attribut)


    ############################
    # Public API
    ############################
    def exists(self, uri):
        g_file = self._get_g_file(uri)
        return g_file.query_exists()


    def is_file(self, uri):
        g_file = self._get_g_file(uri)
        return _is_file(g_file)


    def is_folder(self, uri):
        g_file = self._get_g_file(uri)
        return _is_folder(g_file)


    def can_read(self, uri):
        return self._can_x(uri, FILE_ATTRIBUTE_ACCESS_CAN_READ)


    def can_write(self, uri):
        return self._can_x(uri, FILE_ATTRIBUTE_ACCESS_CAN_WRITE)


    def make_file(self, uri):
        g_file = self._get_g_file(uri)

        # Make the parent's directory
        _make_directory_with_parents(g_file.get_parent())

        return g_file.create()


    def make_folder(self, uri):
        g_file = self._get_g_file(uri)
        # XXX g_file_make_directory_with_parents is not yet implemented!!
        _make_directory_with_parents(g_file)


    def get_ctime(self, uri):
        return self._get_xtime(uri, FILE_ATTRIBUTE_TIME_CHANGED)


    def get_mtime(self, uri):
        return self._get_xtime(uri, FILE_ATTRIBUTE_TIME_MODIFIED)


    def get_atime(self, uri):
        return self._get_xtime(uri, FILE_ATTRIBUTE_TIME_ACCESS)


    def get_mimetype(self, uri):
        g_file = self._get_g_file(uri)

        info = g_file.query_info(FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        content_type = info.get_attribute_as_string(
                            FILE_ATTRIBUTE_STANDARD_CONTENT_TYPE)
        return content_type_get_mime_type(content_type)


    def get_size(self, uri):
        g_file = self._get_g_file(uri)
        info = g_file.query_info(FILE_ATTRIBUTE_STANDARD_SIZE)
        return info.get_attribute_uint64(FILE_ATTRIBUTE_STANDARD_SIZE)


    def open(self, uri, mode=READ):
        g_file = self._get_g_file(uri)

        # A directory => a new Folder ?
        if g_file.query_exists() and _is_folder(g_file):
            return Folder(g_file)

        # Get the Stream
        if mode is READ:
            # XXX can we find a better implementation ?
            # The problem is that a GFileInputStream object
            # doesn't implement all the usual functions of "file"
            # by example, there is no get_lines member.
            return StringIO(g_file.read().read())
        elif mode is WRITE:
            return g_file.replace('', False)
        elif mode is APPEND:
            return g_file.append_to()
        # XXX Finish me
        elif mode is READ_WRITE:
            raise NotImplementedError


    def remove(self, uri):
        g_file = self._get_g_file(uri)
        _remove(g_file)


    def copy(self, source, target):
        source = self._get_g_file(source)
        target = self._get_g_file(target)

        # Make the target's parent directory
        _make_directory_with_parents(target.get_parent())

        _copy(source, target)


    def move(self, source, target):
        source = self._get_g_file(source)
        target = self._get_g_file(target)

        # Make the target's parent directory
        _make_directory_with_parents(target.get_parent())

        source.move(target)


    def get_names(self, uri='.'):
        g_file = self._get_g_file(uri)
        return _get_names(g_file)


    def traverse(self, uri):
        g_file = self._get_g_file(uri)
        return _traverse(g_file)


    def get_uri(self, reference='.'):
        g_file = self._get_g_file(reference)
        return g_file.get_uri()


    def get_relative_path(self, uri):
        g_file = self._get_g_file(uri)
        if self._folder is None:
            return g_file.get_path()
        return self._folder.get_relative_path(g_file)


######################################################################
# Current Working Directory
######################################################################
vfs = Folder()

