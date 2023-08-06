#!/usr/bin/python

import stat
import logging
import dateutil.parser
import re
import json
import os
import atexit
import resource

from errno          import *
from time           import mktime, time
from argparse       import ArgumentParser
from fuse           import FUSE, Operations, FuseOSError, c_statvfs, \
                           fuse_get_context #, LoggingMixIn
from threading      import Lock, RLock
from collections    import deque
from sys            import argv, exit, excepthook
from tempfile       import NamedTemporaryFile
from os             import unlink

from gdrivefs.utility   import get_utility
from gdrivefs.gdtool    import drive_proxy, NormalEntry, get_auth, AccountInfo
from gdrivefs.errors    import ExportFormatError, AuthorizationFailureError
from gdrivefs.change    import get_change_manager
from gdrivefs.timer     import Timers
from gdrivefs.cache     import PathRelations, EntryCache, \
                               CLAUSE_ENTRY, CLAUSE_PARENT, CLAUSE_CHILDREN, \
                               CLAUSE_ID, CLAUSE_CHILDREN_LOADED
from gdrivefs.conf      import Conf

class _NotFoundError(Exception):
    pass

class _EntryNoLongerCachedError(Exception):
    pass

def _strip_export_type(path, set_mime=True):

    rx = re.compile('(#([a-zA-Z0-9]+))?(\$)?$')
    matched = rx.search(path.encode('ASCII'))

    extension = None
    mime_type = None
    just_info = None

    if matched:
        fragment = matched.group(0)
        extension = matched.group(2)
        just_info = (matched.group(3) == '$')

        if fragment:
            path = path[:-len(fragment)]

        if not extension:
            extension_rx = re.compile('\.([a-zA-Z0-9]+)$')
            matched = extension_rx.search(path.encode('ASCII'))

            if matched:
                extension = matched.group(1)

        if extension:
            logging.info("User wants to export to extension [%s]." % 
                         (extension))

            if set_mime:
                try:
                    mime_type = get_utility().get_first_mime_type_by_extension \
                                    (extension)
                except:
                    logging.warning("Could not render a mime-type for "
                                    "prescribed extension [%s], for read." % 
                                    (extension))

                if mime_type:
                    logging.info("We have been told to export using mime-type "
                                 "[%s]." % (mime_type))

    return (path, extension, just_info, mime_type)

def _split_path(filepath):
    """Completely process and distill the requested file-path. The filename can"
    be padded for adjust what's being requested. This will remove all such 
    information, and return the actual file-path along with the extra meta-
    information.
    """

    # Remove any export-type that this file-path might've been tagged with.

    try:
        (filepath, extension, just_info, mime_type) = _strip_export_type(filepath)
    except:
        logging.exception("Could not process path [%s] for export-type." % 
                          (filepath))
        raise

    # Split the file-path into a path and a filename.

    (path, filename) = os.path.split(filepath)

    if path[0] != '/' or filename == '':
        message = ("Could not create directory with badly-formatted "
                   "file-path [%s]." % (filepath))

        logging.error(message)
        raise ValueError(message)

    # Lookup the file, as it was listed, in our cache.

    path_relations = PathRelations.get_instance()

    try:
        parent_clause = path_relations.get_clause_from_path(path)
    except:
        logger.exception("Could not get clause from path [%s]." % (path))
        raise _NotFoundError()

    if not parent_clause:
        logging.debug("Path [%s] does not exist for split." % (path))
        raise _NotFoundError()

    parent_entry = parent_clause[CLAUSE_ENTRY]

    # Strip a prefixing dot, if present.

    if filename[0] == '.':
        is_hidden = True
#        filename = filename[1:]

    else:
        is_hidden = False

    logging.debug("File-path [%s] dereferenced to parent with ID [%s], path "
                  "[%s], filename [%s], extension [%s], mime-type [%s], "
                  "is_hidden [%s], and just-info [%s]." % 
                  (filepath, parent_entry.id, path, filename, extension, 
                   mime_type, is_hidden, just_info))

    return (parent_clause, path, filename, extension, mime_type, is_hidden, 
            just_info)

class _DisplacedFile(object):
    __log = None
    normalized_entry = None
    file_size = 1000

    def __init__(self, normalized_entry):
        self.__log = logging.getLogger().getChild('DisFile')
    
        if normalized_entry.__class__ != NormalEntry:
            raise Exception("_DisplacedFile can not wrap a non-NormalEntry object.")

        self.normalized_entry = normalized_entry

    def deposit_file(self, mime_type=None):
        """Write the file to a temporary path, and present a stub (JSON) to the 
        user. This is the only way of getting files that don't have a definite 
        filesize.
        """

        if not mime_type:
            mime_type = self.normalized_entry.normalized_mime_type

        try:
            (temp_file_path, length) = drive_proxy('download_to_local', 
                                     normalized_entry=self.normalized_entry,
                                     mime_type=mime_type)
        except:
            self.__log.exception("Could not localize displaced file with entry "
                              "having ID [%s]." % (self.normalized_entry.id))
            raise

        try:
            return self.get_stub(mime_type, length, temp_file_path)
        except:
            self.__log.exception("Could not build stub.")
            raise

    def get_stub(self, mime_type=None, file_size=0, file_path=None):

        if not mime_type:
            mime_type = self.normalized_entry.normalized_mime_type

        stub_data = {
                'EntryId':              self.normalized_entry.id,
                'OriginalMimeType':     self.normalized_entry.mime_type,
                'ExportTypes':          self.normalized_entry.download_links.keys(),
                'Title':                self.normalized_entry.title,
                'Labels':               self.normalized_entry.labels,
                'FinalMimeType':        mime_type,
                'Length':               file_size,
                'Displaceable':         self.normalized_entry.requires_displaceable,
                'ImageMediaMetadata':   self.normalized_entry.image_media_metadata
            }

        if file_path:
            stub_data['FilePath'] = file_path

        try:
            result = json.dumps(stub_data)
            padding = (' ' * (self.file_size - len(result) - 1))

            return ("%s%s\n" % (result, padding))
        except:
            self.__log.exception("Could not serialize stub-data.")
            raise


class _OpenedManager(object):
    __log = None
    opened = { }
    opened_lock = RLock()
    fh_counter = 1

    @staticmethod
    def get_instance():
        with _OpenedManager.singleton_lock:
            if _OpenedManager.instance == None:
                try:
                    _OpenedManager.instance = _OpenedManager()
                except:
                    self.__log.exception("Could not create singleton instance of "
                                      "_OpenedManager.")
                    raise

            return _OpenedManager.instance

    def __init__(self):
        self.__log = logging.getLogger().getChild('OpenMan')

    def __get_max_handles(self):

        return resource.getrlimit(resource.RLIMIT_NOFILE)[0]

    def get_new_handle(self):
        """Get a handle for a file that's about to be opened. Note that the 
        handles start at (1), so there are a lot of "+ 1" occurrences below.
        """

        max_handles = self.__get_max_handles()

        with self.opened_lock:
            if len(self.opened) >= (max_handles + 1):
                raise FuseOSError(EMFILE)

            safety_counter = max_handles
            while safety_counter >= 1:
                self.fh_counter += 1

                if self.fh_counter >= (max_handles + 1):
                    self.fh_counter = 1

                if self.fh_counter not in self.opened:
                    return self.fh_counter
                
        message = "Could not allocate new file handle. Safety breach."

        self.__log.error(message)
        raise Exception(message)

    def add(self, opened_file, fh=None):
        """Registered an _OpenedFile object."""

        if opened_file.__class__.__name__ != '_OpenedFile':
            message = "Can only register an _OpenedFile as an opened-file."

            self.__log.error(message)
            raise Exception(message)

        with self.opened_lock:
            if not fh:
                try:
                    fh = self.get_new_handle()
                except:
                    self.__log.exception("Could not acquire handle for "
                                      "_OpenedFile to be registered.")
                    raise

            elif fh in self.opened:
                message = ("Opened-file with file-handle (%d) has already been"
                           " registered." % (opened_file.fh))

                self.__log.error(message)
                raise Exception(message)

            self.opened[fh] = opened_file

            return fh

    def remove_by_fh(self, fh):
        """Remove an opened-file, by the handle."""

        with self.opened_lock:
            self.__log.debug("Closing opened-file with handle (%d)." % (fh))

            if fh not in self.opened:
                message = ("Opened-file with file-handle (%d) is not "
                          "registered (remove_by_fh)." % (fh))

                self.__log.error(message)
                raise Exception(message)

            del self.opened[fh]

    def get_by_fh(self, fh):
        """Retrieve an opened-file, by the handle."""

        with self.opened_lock:
            if fh not in self.opened:
                message = ("Opened-file with file-handle (%d) is not "
                          "registered (get_by_fh)." % (fh))

                self.__log.error(message)
                raise Exception(message)

            return self.opened[fh]

def _annotate(argument_names=[], excluded=[], prefix=''):
    """A decorator for the VFS functions. Displays prefix and suffix 
    information in the logs.
    """

    try:
        log = _annotate.log
    except:
        log = logging.getLogger().getChild('VfsAction')
        _annotate.log = log

    # We use a serial-number so that we can eyeball corresponding pairs of
    # beginning and ending statements in the logs.
    sn = getattr(_annotate, 'sn', 0) + 1
    _annotate.sn = sn

    prefix = ("%s: " % (prefix)) if prefix else ''

    def real_decorator(f):
        def wrapper(*args, **kwargs):
        
            try:
                pid = fuse_get_context()[2]
            except:
                # Just in case.
                pid = 0
        
            log.info("%s>>>>>>>>>> %s(%d) >>>>>>>>>> (%d)" % 
                     (prefix, f.__name__, sn, pid))
        
            if args or kwargs:
                condensed = {}
                for i in xrange(len(args)):
                    # Skip the 'self' argument.
                    if i == 0:
                        continue
                
                    if i - 1 >= len(argument_names):
                        break

                    condensed[argument_names[i - 1]] = args[i]

                for k, v in kwargs.iteritems():
                    condensed[k] = v

                values_nice = [("%s= [%s]" % (k, v)) for k, v \
                                                     in condensed.iteritems() \
                                                     if k not in excluded]
                values_string = '  '.join(values_nice)

                log.debug("DATA: %s" % (values_string))

            suffix = ''

            try:
                result = f(*args, **kwargs)
            except Exception as e:
                suffix = (' (E(%s): "%s")' % (e.__class__.__name__, str(e)))
                raise
            finally:
                log.info("%s<<<<<<<<<< %s(%d) (%d)%s" % 
                         (prefix, f.__name__, sn, pid, suffix))
            
            return result
        return wrapper
    return real_decorator

_OpenedManager.instance = None
_OpenedManager.singleton_lock = Lock()

class _OpenedFile(object):
    """This class describes a single open file, and manages changes."""

    __log = None

    entry_id        = None
    path            = None
    filename        = None
    is_hidden       = None
    mime_type       = None

    file_path       = None
    cache           = None
    temp_file_path  = None
    last_file_size  = None
    buffer          = None

    updates         = deque()
    update_lock     = Lock()
    download_lock   = Lock()

    @staticmethod
    def create_for_requested_filepath(filepath):
        """Process the file/path that was requested (potential export-type 
        directive, dot-prefix, etc..), and build an opened-file object using 
        the information.
        """

        self.__log.debug("Creating _OpenedFile for [%s]." % (filepath))

        # Process/distill the requested file-path.

        try:
            (parent_clause, path, filename, extension, mime_type, is_hidden, \
             just_info) = _split_path(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (create).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not split path [%s] (create)." % 
                              (filepath))
            raise

        # Look-up the requested entry.

        path_relations = PathRelations.get_instance()

        try:
            entry_clause = path_relations.get_clause_from_path(filepath)
        except:
            self.__log.exception("Could not try to get clause from path [%s] "
                              "(_OpenedFile)." % (filepath))
            raise FuseOSError(EIO)

        if not entry_clause:
            self.__log.debug("Path [%s] does not exist for stat()." % (path))
            raise FuseOSError(ENOENT)

        # Build the object.

        try:
            return _OpenedFile(entry_clause[CLAUSE_ID], path, filename, is_hidden, mime_type)
        except:
            self.__log.exception("Could not create _OpenedFile for requested file"
                              " [%s]." % (filepath))
            raise

    def __init__(self, entry_id, path, filename, is_hidden, mime_type):

        self.__log = logging.getLogger().getChild('OpenFile')

        self.__log.info("Opened-file object created for entry-ID [%s] and path "
                     "(%s)." % (entry_id, path))

        self.entry_id   = entry_id
        self.path       = path
        self.filename   = filename
        self.is_hidden  = is_hidden
        self.mime_type  = mime_type
        self.cache      = EntryCache.get_instance().cache

    def __get_entry_or_raise(self):
        """We can never be sure that the entry will still be known to the 
        system. Grab it and throw an error if it's not available.
        """

        self.__log.debug("Retrieving entry for opened-file with entry-ID [%s]." % 
                      (self.entry_id))

        try:
            return self.cache.get(self.entry_id)
        except:
            self.__log.exception("Could not retrieve entry with ID [%s] for the "
                              "opened-file." % (self.entry_id))
            raise 

    @_annotate(prefix='OF')
    def __load_base_from_remote(self):
        """Download the data for the file that we represent."""

        self.__log.debug("Retrieving entry for load_base_from_remote.")

        try:
            entry = self.__get_entry_or_raise()
        except:
            self.__log.exception("Could not get entry with ID [%s] for "
                              "write-flush." % (self.entry_id))
            raise

        with self.download_lock:
            # Get the current version of the write-cache file, or note that we 
            # don't have it.

            self.__log.debug("Checking state of current write-cache file.")

            update_cached_file = True
# TODO: Deprecate this. .buffer is only referenced from read().
            if not self.buffer:
                try:
                    stat = os.stat(self.temp_file_path)
                except:
                    self.__log.debug("Write-cache file [%s] does not seem to"
                                  "exist." % (self.temp_file_path))
                else:
                    # Our buffer always matches the write-cache file, and 
                    # because our "entry" object is a reference to our cache 
                    # and our cache is always going to be up to date because of
                    # our change-management framework, we'll only do an update 
                    # when one is needed, up to within the resolution of our 
                    # change checks.
                    if entry.modified_date_epoch == stat.st_mtime:
                        update_cached_file = False

            # We don't yet have a copy of the file, or it has been changed by 
            # someone else.

            if not update_cached_file:
                self.__log.debug("Write-cache file [%s] is already up-to-date." %
                              (self.temp_file_path))
                return

            self.__log.info("Updating write-cache file for entry with ID [%s] and"
                         " mime-type [%s]." % (entry.id, self.mime_type))

            # The output path is predictable. It shouldn't change.

            mime_type = self.mime_type if self.mime_type else entry.normalized_mime_type

            try:
                (temp_file_path, length) = \
                    drive_proxy('download_to_local', 
                                    normalized_entry=entry,
                                    mime_type=mime_type,
                                    allow_cache=False)
            except (ExportFormatError):
                raise FuseOSError(ENOENT)
            except:
                self.__log.exception("Could not localize file with entry having "
                                  "ID [%s]." % (self.entry_id))
                raise

            self.temp_file_path = temp_file_path
            self.last_file_size = length

            # Load our buffer.

            self.__log.debug("Reading write-cache file.")

            with open(self.temp_file_path, 'rb') as f:
                # Read the locally cached file in.

                try:
                    self.buffer = f.read()
                except:
                    self.__log.exception("Could not read current cached file into buffer.")
                    raise

    @_annotate(['offset', 'data'], ['data'], 'OF')
    def add_update(self, offset, data):
        """Queue an update to this file."""

        self.__marker('add_update', { 'offset': offset, 
                                    'actual_length': len(data) })

        with self.update_lock:
            self.updates.append((offset, data))

        self.__log.debug("(%d) updates have been queued." % (len(self.updates)))

    @_annotate(prefix='OF')
    def flush(self):
        """The OS wants to effect any changes made to the file."""

        #print("Flushing (%d) updates." % (len(self.updates)))

        self.__log.debug("Retrieving entry for write-flush.")

        try:
            entry = self.__get_entry_or_raise()
        except:
            self.__log.exception("Could not get entry with ID [%s] for "
                              "write-flush." % (self.entry_id))
            raise
    
        with self.update_lock:
            if not self.updates:
                self.__log.debug("Flush will be skipped due to empty write-"
                              "queue.")
                return
# We no longer apply the updates to the existing data. We suspect that we're
# always fed complete data, or we'd never be able to determine truncation.
#            self.__log.debug("Checking write-cache file (flush).")
#
#            try:
#                self.__load_base_from_remote()
#            except:
#                self.__log.exception("Could not load write-cache file [%s]." % 
#                                  (self.temp_file_path))
#                raise

            # Apply updates to the data.

            self.__log.debug("Applying (%d) updates." % (len(self.updates)))

            i = 0
            buffer = ''
            while self.updates:
#                print("Applying update (%d)." % (i))
            
                (offset, data) = self.updates.popleft()
                self.__log.debug("Applying update (%d) at offset (%d) with data-"
                              "length (%d)." % (i, offset, len(data)))

                right_fragment_start = offset + len(data)

#                self.buffer = self.buffer[0:offset] + data + \
#                                self.buffer[right_fragment_start:]
                buffer = buffer[0:offset] + data + \
                                buffer[right_fragment_start:]

                i += 1

            # Write back out to the temporary file.

            self.__log.debug("Writing buffer to temporary file.")
# TODO: Make sure to uncache the temp data if self.temp_file_path is not None.

            if self.temp_file_path:
                is_temp = False
                write_file_path = self.temp_file_path
            else:
                is_temp = True
            
                with NamedTemporaryFile(delete=False) as f:
                    write_file_path = f.name
                    f.write(buffer)

            # Push to GD.

            self.__log.debug("Pushing (%d) bytes for entry with ID from [%s] to "
                          "GD for file-path [%s]." % (len(buffer), 
                                                      entry.id, 
                                                      write_file_path))

#            print("Sending updates.")

            try:
                entry = drive_proxy('update_entry', normalized_entry=entry, 
                                    filename=entry.title, 
                                    data_filepath=write_file_path, 
                                    mime_type=entry.mime_type, 
                                    parents=entry.parents, 
                                    is_hidden=self.is_hidden)
            except:
                self.__log.exception("Could not localize displaced file with "
                                  "entry having ID [%s]." % 
                                  (entry.id))
                raise

            if not is_temp:
                unlink(write_file_path)
            else:
                # Update the write-cache file to the official mtime. We won't 
                # redownload it on the next flush if it wasn't changed, elsewhere.

                self.__log.debug("Updating local write-cache file to official mtime "
                              "[%s]." % (entry.modified_date_epoch))

                try:
                    os.utime(write_file_path, (entry.modified_date_epoch, 
                                               entry.modified_date_epoch))
                except:
                    self.__log.exception("Could not update mtime of write-cache [%s] "
                                      "for entry with ID [%s], post-flush." % 
                                      (entry.modified_date_epoch, entry.id))
                    raise

        # Immediately update our current cached entry.

        self.__log.debug("Update successful. Updating local cache.")

        path_relations = PathRelations.get_instance()

        try:
            path_relations.register_entry(entry)
        except:
            self.__log.exception("Could not register updated file in cache.")
            raise

        self.__log.info("Update complete on entry with ID [%s]." % (entry.id))

    @_annotate(['offset', 'length'], prefix='OF')
    def read(self, offset, length):
        
        self.__log.debug("Checking write-cache file (flush).")

        try:
            self.__load_base_from_remote()
        except:
            self.__log.exception("Could not load write-cache file [%s]." % 
                              (self.temp_file_path))
            raise

        return self.buffer[offset:length]

# TODO: make sure strip_extension and split_path are used when each are relevant
# TODO: make sure create path reserves a file-handle, uploads the data, and then registers the open-file with the file-handle.
# TODO: make sure to finish the opened-file helper factory.

class _GDriveFS(Operations):#LoggingMixIn,
    """The main filesystem class."""

    __log = None

    def __init__(self):
        Operations.__init__(self)

        self.__log = logging.getLogger().getChild('GD_VFS')

    def __register_open_file(self, fh, path, entry_id):

        with self.fh_lock:
            self.open_files[fh] = (entry_id, path)

    def __deregister_open_file(self, fh):

        with self.fh_lock:
            try:
                file_info = self.open_files[fh]
            except:
                self.__log.exception("Could not deregister invalid file-handle "
                                  "(%d)." % (fh))
                raise

            del self.open_files[fh]
            return file_info

    def __get_open_file(self, fh):

        with self.fh_lock:
            try:
                return self.open_files[fh]
            except:
                self.__log.exception("Could not retrieve on invalid file-handle "
                                  "(%d)." % (fh))
                raise

    @_annotate(['raw_path', 'fh'])
    def getattr(self, raw_path, fh=None):
        """Return a stat() structure."""
# TODO: Implement handle.

        try:
            (path, extension, just_info, mime_type) = _strip_export_type \
                                                        (raw_path, True)
        except:
            self.__log.exception("Could not process export-type directives.")
            raise FuseOSError(EIO)

        path_relations = PathRelations.get_instance()

        try:
            entry_clause = path_relations.get_clause_from_path(path)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (getattr).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not try to get clause from path [%s] "
                              "(getattr)." % (path))
            raise FuseOSError(EIO)

        if not entry_clause:
            self.__log.debug("Path [%s] does not exist for stat()." % (path))
            raise FuseOSError(ENOENT)

        effective_permission = 0o444
        normalized_entry = entry_clause[0]

        entry = entry_clause[0]

        # If the user has required info, we'll treat folders like files so that 
        # we can return the info.
        is_folder = get_utility().is_directory(entry) and not just_info

        if entry.editable:
            effective_permission |= 0o222

        stat_result = { "st_mtime": entry.modified_date_epoch }
        
        stat_result["st_size"] = _DisplacedFile(entry).file_size \
                                    if (is_folder or \
                                            entry.requires_displaceable) \
                                    else entry.file_size

        if is_folder:
            effective_permission |= 0o111
            stat_result["st_mode"] = (stat.S_IFDIR | effective_permission)

            stat_result["st_nlink"] = 2
        else:
            stat_result["st_mode"] = (stat.S_IFREG | effective_permission)
            stat_result["st_nlink"] = 1

        return stat_result

    @_annotate(['path', 'offset'])
    def readdir(self, path, offset):
        """A generator returning one base filename at a time."""

        # We expect "offset" to always be (0).
        if offset != 0:
            self.__log.warning("readdir() has been invoked for path [%s] and non-"
                            "zero offset (%d). This is not allowed." % 
                            (path, offset))

# TODO: Once we start working on the cache, make sure we don't make this call, 
#       constantly.

        path_relations = PathRelations.get_instance()

        self.__log.debug("Listing files.")

        try:
            entry_clause = path_relations.get_clause_from_path(path)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (readdir).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not get clause from path [%s] "
                              "(readdir)." % (path))
            raise FuseOSError(EIO)

        if not entry_clause:
            self.__log.debug("Path [%s] does not exist for readdir()." % (path))
            raise FuseOSError(ENOENT)

        try:
            filenames = path_relations.get_child_filenames_from_entry_id \
                            (entry_clause[3])
        except:
            self.__log.exception("Could not render list of filenames under path "
                             "[%s]." % (path))
            raise FuseOSError(EIO)

        filenames[0:0] = ['.','..']

        for filename in filenames:
            yield filename

    @_annotate(['raw_path', 'length', 'offset', 'fh'])
    def read(self, raw_path, length, offset, fh):

#
#        # Fetch the file to a local, temporary file.
#
#        if normalized_entry.requires_displaceable or just_info:
#            self.__log.info("Doing displaced-file download of entry with ID "
#                         "[%s]." % (entry_id))
#
#            try:
#                displaced = _DisplacedFile(normalized_entry)
#            except:
#                self.__log.exception("Could not wrap entry in _DisplacedFile.")
#                raise
#
#            try:
#                if just_info:
#                    self.__log.debug("Info for file was requested, rather than "
#                                  "the file itself.")
#                    return displaced.get_stub(mime_type)
#                else:
#                    self.__log.debug("A displaceable file was requested.")
#                    return displaced.deposit_file(mime_type)
#            except:
#                self.__log.exception("Could not do displaced-file download.")
#                raise
#
#        else:
#            self.__log.info("Downloading entry with ID [%s] for path [%s]." % 
#                         (entry_id, path))

        try:
            opened_file = _OpenedManager.get_instance().get_by_fh(fh)
        except:
            self.__log.exception("Could not retrieve _OpenedFile for handle with "
                              "ID (%d) (read)." % (fh))
            raise FuseOSError(EIO)

        try:
            return opened_file.read(offset, length)
        except:
            self.__log.exception("Could not read data.")
            raise FuseOSError(EIO)

    @_annotate(['filepath', 'mode'])
    def mkdir(self, filepath, mode):
        """Create the given directory."""

# TODO: Implement the "mode".

        try:
            (parent_clause, path, filename, extension, mime_type, is_hidden, \
             just_info) = _split_path(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (mkdir).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not split path [%s] (mkdir)." % 
                              (filepath))
            raise FuseOSError(EIO)

        self.__log.debug("Creating directory [%s] under [%s]." % (filename, path))

        try:
            entry = drive_proxy('create_directory', filename=filename, 
                        parents=[parent_clause[0].id], is_hidden=is_hidden)
        except:
            self.__log.exception("Could not create directory with name [%s] and "
                              "parent with ID [%s]." % (filename, 
                                                        parent_clause[0].id))
            raise FuseOSError(EIO)

        self.__log.info("Directory [%s] created as ID [%s]." % (filepath, 
                     entry.id))

        #parent_clause[4] = False

        path_relations = PathRelations.get_instance()

        try:
            path_relations.register_entry(entry)
        except:
            self.__log.exception("Could not register new directory in cache.")
            raise FuseOSError(EIO)

    @_annotate(['filepath', 'mode'])
    def create(self, filepath, mode):
        """Create a new file. This always precedes a write.
        
        We don't implement "mode" (permissions) because the model doesn't agree 
        with GD.
        """
# TODO: Fail if it already exists.

        self.__log.debug("Splitting file-path [%s] for create." % (filepath))

        try:
            (parent_clause, path, filename, extension, mime_type, is_hidden, \
             just_info) = _split_path(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (create).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not split path [%s] (create)." % 
                              (filepath))
            raise FuseOSError(EIO)

        self.__log.debug("Acquiring file-handle.")

        try:
            fh = _OpenedManager.get_instance().get_new_handle()
        except:
            self.__log.exception("Could not acquire file-handle for create of "
                              "[%s]." % (filepath))
            raise FuseOSError(EIO)

        self.__log.debug("Creating empty file [%s] under parent with ID [%s]." % 
                      (filename, parent_clause[3]))

        try:
            entry = drive_proxy('create_file', filename=filename, 
                                data_filepath='/dev/null', 
                                parents=[parent_clause[3]], 
                                is_hidden=is_hidden)
        except:
            self.__log.exception("Could not create empty file [%s] under parent "
                              "with ID [%s]." % (filename, parent_clause[3]))
            raise FuseOSError(EIO)

        self.__log.debug("Registering created file in cache.")

        path_relations = PathRelations.get_instance()

        try:
            path_relations.register_entry(entry)
        except:
            self.__log.exception("Could not register created file in cache.")
            raise FuseOSError(EIO)

        self.__log.debug("Building _OpenedFile object for created file.")

        try:
            opened_file = _OpenedFile(entry.id, path, filename, is_hidden, mime_type)
        except:
            self.__log.exception("Could not create _OpenedFile object for "
                              "created file.")
            raise FuseOSError(EIO)

        self.__log.debug("Registering _OpenedFile object with handle (%d), path "
                      "[%s], and ID [%s]." % (fh, filepath, entry.id))

        try:
            _OpenedManager.get_instance().add(opened_file, fh=fh)
        except:
            self.__log.exception("Could not register _OpenedFile for created "
                              "file.")
            raise FuseOSError(EIO)

        self.__log.debug("File created, opened, and completely registered.")

        return fh

    @_annotate(['filepath', 'flags'])
    def open(self, filepath, flags):
# TODO: Fail if does not exist and the mode is read only.

        self.__log.debug("Building _OpenedFile object for file being opened.")

        try:
            opened_file = _OpenedFile.create_for_requested_filepath(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (open).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not create _OpenedFile object for "
                              "opened filepath.")
            raise FuseOSError(EIO)

        self.__log.debug("_OpenedFile object with path [%s] and ID [%s]." % 
                      (filepath, opened_file.entry_id))

        try:
            fh = _OpenedManager.get_instance().add(opened_file)
        except:
            self.__log.exception("Could not register _OpenedFile for opened "
                              "file.")
            raise FuseOSError(EIO)

        self.__log.debug("File opened.")

        return fh

    @_annotate(['filepath', 'fh'])
    def release(self, filepath, fh):
        """Close a file."""

        try:
            _OpenedManager.get_instance().remove_by_fh(fh)
        except:
            self.__log.exception("Could not remove _OpenedFile for handle with ID"
                              "(%d) (release)." % (fh))
            raise FuseOSError(EIO)

    @_annotate(['filepath', 'data', 'offset', 'fh'], ['data'])
    def write(self, filepath, data, offset, fh):

        try:
            opened_file = _OpenedManager.get_instance().get_by_fh(fh=fh)
        except:
            self.__log.exception("Could not get _OpenedFile (write).")
            raise FuseOSError(EIO)

        try:
            opened_file.add_update(offset, data)
        except:
            self.__log.exception("Could not queue file-update.")
            raise FuseOSError(EIO)

        return len(data)

    @_annotate(['filepath', 'fh'])
    def flush(self, filepath, fh):
        
        try:
            opened_file = _OpenedManager.get_instance().get_by_fh(fh=fh)
        except:
            self.__log.exception("Could not get _OpenedFile (flush).")
            raise FuseOSError(EIO)

        try:
            opened_file.flush()
        except:
            self.__log.exception("Could not flush local updates.")
            raise FuseOSError(EIO)

    @_annotate(['filepath'])
    def rmdir(self, filepath):
        """Remove a directory."""

        path_relations = PathRelations.get_instance()

        self.__log.debug("Removing directory [%s]." % (filepath))

        try:
            entry_clause = path_relations.get_clause_from_path(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (rmdir).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not get clause from file-path [%s] "
                              "(rmdir)." % (filepath))
            raise FuseOSError(EIO)

        if not entry_clause:
            self.__log.error("Path [%s] does not exist for rmdir()." % (filepath))
            raise FuseOSError(ENOENT)

        entry_id = entry_clause[CLAUSE_ID]
        normalized_entry = entry_clause[CLAUSE_ENTRY]

        # Check if not a directory.

        self.__log.debug("Ensuring it is a directory.")

        if not normalized_entry.is_directory:
            self.__log.error("Can not rmdir() non-directory [%s] with ID [%s].", filepath, entry_id)
            raise FuseOSError(ENOTDIR)

        # Ensure the folder is empty.

        self.__log.debug("Checking if empty.")

        try:
            found = drive_proxy('get_children_under_parent_id', 
                                parent_id=entry_id,
                                max_results=1)
        except:
            self.__log.exception("Could not determine if directory to be removed "
                              "has children." % (entry_id))
            raise FuseOSError(EIO)

        if found:
            raise FuseOSError(ENOTEMPTY)

        self.__log.debug("Doing remove of directory [%s] with ID [%s]." % 
                      (filepath, entry_id))

        try:
            drive_proxy('remove_entry', normalized_entry=normalized_entry)
        except (NameError):
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not remove directory [%s] with ID [%s]." % 
                              (filepath, entry_id))
            raise FuseOSError(EIO)
# TODO: Remove from cache.
        self.__log.debug("Directory removal complete.")

    # Not supported. Google Drive doesn't fit within this model.
    @_annotate(['filepath', 'mode'])
    def chmod(self, filepath, mode):

        raise FuseOSError(EPERM)

    # Not supported. Google Drive doesn't fit within this model.
    @_annotate(['filepath', 'uid', 'gid'])
    def chown(self, filepath, uid, gid):

        raise FuseOSError(EPERM)

    # Not supported.
    @_annotate(['target', 'source'])
    def symlink(self, target, source):

        raise FuseOSError(EPERM)

    # Not supported.
    @_annotate(['filepath'])
    def readlink(self, filepath):

        raise FuseOSError(EPERM)

    @_annotate(['filepath'])
    def statfs(self, filepath):
        """Return filesystem metrics.

        The given file-path seems to always be '/'.

        REF: http://www.ibm.com/developerworks/linux/library/l-fuse/
        REF: http://stackoverflow.com/questions/4965355/converting-statvfs-to-percentage-free-correctly
        """

        block_size = 512

        try:
            account_info = AccountInfo.get_instance()
            total = account_info.quota_bytes_total / block_size
            used = account_info.quota_bytes_used / block_size
            free = total - used
        except:
            self.__log.exception("Could not get account-info.")
            raise FuseOSError(EIO)

        return {
            # Optimal transfer block size.
            'f_bsize': block_size,

            # Total data blocks in file system.
            'f_blocks': used,

            # Fragment size.
#            'f_frsize': block_size,

            # Free blocks in filesystem.
#            'f_bfree': free,

            # Free blocks avail to non-superuser.
            'f_bavail': free

            # Total file nodes in filesystem.
#            'f_files': 0,

            # Free file nodes in filesystem.
#            'f_ffree': 0,

            # Free inodes for unprivileged users.
#            'f_favail': 0
        }

# TODO: Finish this.
    @_annotate(['old', 'new'])
    def rename(self, old, new):
        pass

# TODO: Finish this.
    @_annotate(['path', 'length', 'fh'])
    def truncate(self, path, length, fh=None):
        pass

    @_annotate(['filepath'])
    def unlink(self, filepath):
        """Remove a file."""

        path_relations = PathRelations.get_instance()

        self.__log.debug("Removing file [%s]." % (filepath))

        try:
            entry_clause = path_relations.get_clause_from_path(filepath)
        except _NotFoundError:
            self.__log.exception("Could not process [%s] (unlink).")
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not get clause from file-path [%s] "
                              "(unlink)." % (filepath))
            raise FuseOSError(EIO)

        if not entry_clause:
            self.__log.error("Path [%s] does not exist for unlink()." % (filepath))
            raise FuseOSError(ENOENT)

        entry_id = entry_clause[CLAUSE_ID]
        normalized_entry = entry_clause[CLAUSE_ENTRY]

        # Check if a directory.

        self.__log.debug("Ensuring it is a file (not a directory).")

        if normalized_entry.is_directory:
            self.__log.error("Can not unlink() directory [%s] with ID [%s]. Must be file.", filepath, entry_id)
            raise FuseOSError(errno.EISDIR)

        self.__log.debug("Doing remove of directory [%s] with ID [%s]." % 
                      (filepath, entry_id))

        try:
            drive_proxy('remove_entry', normalized_entry=normalized_entry)
        except (NameError):
            raise FuseOSError(ENOENT)
        except:
            self.__log.exception("Could not remove file [%s] with ID [%s]." % 
                              (filepath, entry_id))
            raise FuseOSError(EIO)

# TODO: Remove from cache.

        self.__log.debug("File removal complete.")

# TODO: Finish this.
    @_annotate(['path', 'times'])
    def utimens(self, path, times=None):
        """Set the file times."""

        pass
#        now = time()
#        atime, mtime = times if times else (now, now)

    @_annotate(['path'])
    def init(self, path):
        """Called on filesystem mount. Path is always /."""

        get_change_manager().mount_init()

    @_annotate(['path'])
    def destroy(self, path):
        """Called on filesystem destruction. Path is always /."""

        get_change_manager().mount_destroy()

def set_auth_cache_filepath(auth_storage_filepath):
    Conf.set('auth_cache_filepath', auth_storage_filepath)

def mount(auth_storage_filepath, mountpoint, debug=None, nothreads=None, option_string=None):

    fuse_opts = { }

    if option_string:
        for opt_parts in [ opt.split('=', 1) for opt in option_string.split(',') ]:
            k = opt_parts[0]

            # We need to present a bool type for on/off flags. Since all we
            # have are strings, we'll convert anything with a 'True' or 'False'
            # to a bool, or anything with just a key to True.
            if len(opt_parts) == 2:
                v = opt_parts[1]

                if v == 'True':
                    v = True
                elif v == 'False':
                    v = False
            else:
                v = True

            # We have a list of provided options. See which match against our 
            # application options.

            logging.info("Setting option [%s] to [%s]." % (k, v))

            try:
                Conf.set(k, v)
            except (KeyError) as e:
                fuse_opts[k] = v
            except:
                logging.exception("Could not set option [%s]. It is probably invalid." % (k))
                raise

    # Assume that any option that wasn't an application option is a FUSE 
    # option. The Python-FUSE interface that we're using is beautiful/elegant,
    # but there's no help support. The user is just going to have to know the
    # options.

    set_auth_cache_filepath(auth_storage_filepath)

    # How we'll appear in diskfree, mtab, etc..
    name = ("gdfs(%s)" % (auth_storage_filepath))

    fuse = FUSE(_GDriveFS(), mountpoint, debug=False, foreground=debug, 
                nothreads=nothreads, fsname=name, **fuse_opts)

def load_mount_parser_args(parser):
    parser.add_argument('auth_storage_file', help='Authorization storage file')
    parser.add_argument('mountpoint', help='Mount point')
    parser.add_argument('-d', '--debug', help='Debug mode',
                        action='store_true', required=False)
    parser.add_argument('-o', '--opt', help='Mount options',
                        action='store', required=False,
                        nargs=1)

def main():
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(help='subcommand help')
    parser_auth = subparsers.add_parser('auth', help='Authorization subcommand.')
    
    auth_xor = parser_auth.add_mutually_exclusive_group(required=True)
    auth_xor.add_argument('-u', '--url', help='Get an authorization URL.', 
                          action='store_true')
    auth_xor.add_argument('-a', '--auth', nargs=2,
                          metavar=('auth_storage_file', 'authcode'), 
                          help='Register an authorization-code from Google '
                          'Drive.')

    mount_auth = subparsers.add_parser('mount', help='Mounting subcommand.')
    load_mount_parser_args(mount_auth)

    args = parser.parse_args()

    # An authorization URL was requested.
    if 'url' in args and args.url:
        try:
            authorize = get_auth()
            url = authorize.step1_get_auth_url()
        except Exception as e:
            print("Could not produce auth-URL: %s" % (e))
            exit()

        print("To authorize FUSE to use your Google Drive account, visit the "
              "following URL to produce an authorization code:\n\n%s\n" % 
              (url))

    # An authorization from the URL needs to be submitted.
    elif 'auth' in args and args.auth:
        (auth_storage_file, authcode) = args.auth

        set_auth_cache_filepath(auth_storage_file)

        try:
            authorize = get_auth()
            authorize.step2_doexchange(authcode)

        except (Exception) as e:
            message = ("Authorization failed: %s" % (str(e)))

            logging.exception(message)
            print(message)
            exit()

        print("Authorization code recorded.")

    # Mount the service.
    elif 'mountpoint' in args and args.mountpoint:

        option_string = args.opt[0] if args.opt else None

        try:
            mount(auth_storage_filepath=args.auth_storage_file, 
                  mountpoint=args.mountpoint, debug=args.debug, 
                  nothreads=args.debug, option_string=option_string)
        except (Exception) as e:
            message = ("Mount failed: %s" % (str(e)))

            logging.exception(message)
            print(message)
            exit()

atexit.register(Timers.get_instance().cancel_all)

if __name__ == "__main__":
    main()


