import json
import logging

from mimetypes import guess_extension
from sys       import getfilesystemencoding

from gdrivefs.conf import Conf

class _DriveUtility(object):
    """General utility functions loosely related to GD."""

    # Mime-types to translate to, if they appear within the "exportLinks" list.
    gd_to_normal_mime_mappings = {
            'application/vnd.google-apps.document':        
                'text/plain',
            'application/vnd.google-apps.spreadsheet':     
                'application/vnd.ms-excel',
            'application/vnd.google-apps.presentation':    
                'application/vnd.ms-powerpoint',
            'application/vnd.google-apps.drawing':         
                'application/pdf',
            'application/vnd.google-apps.audio':           
                'audio/mpeg',
            'application/vnd.google-apps.photo':           
                'image/png',
            'application/vnd.google-apps.video':           
                'video/x-flv'
        }

    # Default extensions for mime-types.
    default_extensions = { 
            'text/plain':                       'txt',
            'application/vnd.ms-excel':         'xls',
            'application/vnd.ms-powerpoint':    'ppt',
            'application/pdf':                  'pdf',
            'audio/mpeg':                       'mp3',
            'image/png':                        'png',
            'video/x-flv':                      'flv'
        }

    _mimetype_directory = u'application/vnd.google-apps.folder'
    local_character_set = getfilesystemencoding()

    def __init__(self):
        self.__load_mappings()

    def __load_mappings(self):
        # Allow someone to override our default mappings of the GD types.

        gd_to_normal_mapping_filepath = \
            Conf.get('gd_to_normal_mapping_filepath')

        try:
            with open(gd_to_normal_mapping_filepath, 'r') as f:
                self.gd_to_normal_mime_mappings.extend(json.load(f))
        except:
            logging.info("No mime-mapping was found.")

        # Allow someone to set file-extensions for mime-types, and not rely on 
        # Python's educated guesses.

        extension_mapping_filepath = Conf.get('extension_mapping_filepath')

        try:
            with open(extension_mapping_filepath, 'r') as f:
                self.default_extensions.extend(json.load(f))
        except:
            logging.info("No extension-mapping was found.")

    def is_directory(self, entry):
        return (entry.mime_type == self._mimetype_directory)

    def get_first_mime_type_by_extension(self, extension):

        found = [ mime_type 
                    for mime_type, temp_extension 
                    in self.default_extensions.iteritems()
                    if temp_extension == extension ]

        if not found:
            return None

        return found[0]

    def get_normalized_mime_type(self, entry):
        
        logging.debug("Deriving mime-type entry with ID [%s]." % (entry.id))

        if entry.is_directory:
            return None

        # Since we're loading from files and also juggling mime-types coming 
        # from Google, we're just going to normalize all of the character-sets 
        # to ASCII. This is reasonable since they're supposed to be standards-
        # based, anyway.
        mime_type = entry.mime_type
        normal_mime_type = None

        # If there's a standard type on the entry, there won't be a list of
        # export options.
        if not entry.download_links:
            normal_mime_type = mime_type

        # If we have a local mapping of the mime-type on the entry to another 
        # mime-type, only use it if that mime-type is listed among the export-
        # types.
        elif mime_type in self.gd_to_normal_mime_mappings:
            normal_mime_type_candidate = \
                self.gd_to_normal_mime_mappings[mime_type]
            if normal_mime_type_candidate in entry.download_links:
                normal_mime_type = normal_mime_type_candidate

        # If we still haven't been able to normalize the mime-type, use the 
        # first available export-link.
        if normal_mime_type == None:
            for temp_mime_type in entry.download_links.iterkeys():
                normal_mime_type = temp_mime_type
                break

        logging.debug("GD MIME [%s] normalized to [%s]." % (mime_type, 
                                                           normal_mime_type))

        return normal_mime_type.encode('ASCII')

    def get_extension(self, entry):
        """Return the filename extension that should be associated with this 
        file.
        """

        logging.debug("Deriving extension for entry with ID [%s]." % 
                      (entry.id))

        try:
            normal_mime_type = self.get_normalized_mime_type(entry)
        except:
            logging.exception("Could not render a mime-type for entry with ID "
                              "[%s]." % (entry.id))
            raise
        
        if not normal_mime_type:
            return None

        # We have an actionable mime-type for the entry, now.

        if normal_mime_type in self.default_extensions:
            file_extension = self.default_extensions[normal_mime_type]
            logging.debug("We had a mapping for mime-type [%s] to extension "
                          "[%s]." % (normal_mime_type, file_extension))

        else:
            try:
                file_extension = guess_extension(normal_mime_type)
            except:
                logging.exception("Could not attempt to derive a file-extension "
                                  "for mime-type [%s]." % (normal_mime_type))
                raise

            if not file_extension:
                return None

            file_extension = file_extension[1:]

            logging.debug("Guessed extension [%s] for mime-type [%s]." % 
                          (file_extension, normal_mime_type))

        return file_extension

    def translate_filename_charset(self, original_filename):
        """Convert the given filename to the correct character set."""
        
        return original_filename.encode(self.local_character_set)

    @property
    def mimetype_directory(self):
        return self._mimetype_directory

def get_utility():
    if get_utility.__instance == None:
        try:
            get_utility.__instance = _DriveUtility()
        except:
            logging.exception("Could not manufacture DriveUtility instance.")
            raise

    return get_utility.__instance

get_utility.__instance = None

