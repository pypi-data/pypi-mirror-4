# Natural Language Toolkit: API for Corpus Readers
#
# Copyright (C) 2001-2012 NLTK Project
# Author: Steven Bird <sb@ldc.upenn.edu>
#         Edward Loper <edloper@gradient.cis.upenn.edu>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

"""
API for corpus readers.
"""

import os
import re
from collections import defaultdict

from nltk.data import PathPointer, FileSystemPathPointer, ZipFilePathPointer
from nltk.sourcedstring import SourcedStringStream

from util import *

class CorpusReader(object):
    """
    A base class for "corpus reader" classes, each of which can be
    used to read a specific corpus format.  Each individual corpus
    reader instance is used to read a specific corpus, consisting of
    one or more files under a common root directory.  Each file is
    identified by its ``file identifier``, which is the relative path
    to the file from the root directory.

    A separate subclass is be defined for each corpus format.  These
    subclasses define one or more methods that provide 'views' on the
    corpus contents, such as ``words()`` (for a list of words) and
    ``parsed_sents()`` (for a list of parsed sentences).  Called with
    no arguments, these methods will return the contents of the entire
    corpus.  For most corpora, these methods define one or more
    selection arguments, such as ``fileids`` or ``categories``, which can
    be used to select which portion of the corpus should be returned.
    """
    def __init__(self, root, fileids, encoding=None, tag_mapping_function=None):
        """
        :type root: PathPointer or str
        :param root: A path pointer identifying the root directory for
            this corpus.  If a string is specified, then it will be
            converted to a ``PathPointer`` automatically.
        :param fileids: A list of the files that make up this corpus.
            This list can either be specified explicitly, as a list of
            strings; or implicitly, as a regular expression over file
            paths.  The absolute path for each file will be constructed
            by joining the reader's root to each file name.
        :param encoding: The default unicode encoding for the files
            that make up the corpus.  The value of ``encoding`` can be any
            of the following:
            - A string: ``encoding`` is the encoding name for all files.
            - A dictionary: ``encoding[file_id]`` is the encoding
              name for the file whose identifier is ``file_id``.  If
              ``file_id`` is not in ``encoding``, then the file
              contents will be processed using non-unicode byte strings.
            - A list: ``encoding`` should be a list of ``(regexp, encoding)``
              tuples.  The encoding for a file whose identifier is ``file_id``
              will be the ``encoding`` value for the first tuple whose
              ``regexp`` matches the ``file_id``.  If no tuple's ``regexp``
              matches the ``file_id``, the file contents will be processed
              using non-unicode byte strings.
            - None: the file contents of all files will be
              processed using non-unicode byte strings.
        :param tag_mapping_function: A function for normalizing or
                simplifying the POS tags returned by the tagged_words()
                or tagged_sents() methods.
        """
        # Convert the root to a path pointer, if necessary.
        if isinstance(root, basestring):
            m = re.match('(.*\.zip)/?(.*)$|', root)
            zipfile, zipentry = m.groups()
            if zipfile:
                root = ZipFilePathPointer(zipfile, zipentry)
            else:
                root = FileSystemPathPointer(root)
        elif not isinstance(root, PathPointer):
            raise TypeError('CorpusReader: expected a string or a PathPointer')

        # If `fileids` is a regexp, then expand it.
        if isinstance(fileids, basestring):
            fileids = find_corpus_fileids(root, fileids)

        self._fileids = fileids
        """A list of the relative paths for the fileids that make up
        this corpus."""

        self._root = root
        """The root directory for this corpus."""

        # If encoding was specified as a list of regexps, then convert
        # it to a dictionary.
        if isinstance(encoding, list):
            encoding_dict = {}
            for fileid in self._fileids:
                for x in encoding:
                    (regexp, enc) = x
                    if re.match(regexp, fileid):
                        encoding_dict[fileid] = enc
                        break
            encoding = encoding_dict

        self._encoding = encoding
        """The default unicode encoding for the fileids that make up
           this corpus.  If ``encoding`` is None, then the file
           contents are processed using byte strings (str)."""
        self._tag_mapping_function = tag_mapping_function

    def __repr__(self):
        if isinstance(self._root, ZipFilePathPointer):
            path = '%s/%s' % (self._root.zipfile.filename, self._root.entry)
        else:
            path = '%s' % self._root.path
        return '<%s in %r>' % (self.__class__.__name__, path)

    def readme(self):
        """
        Return the contents of the corpus README file, if it exists.
        """

        return self.open("README").read()

    def fileids(self):
        """
        Return a list of file identifiers for the fileids that make up
        this corpus.
        """
        return self._fileids

    def abspath(self, fileid):
        """
        Return the absolute path for the given file.

        :type file: str
        :param file: The file identifier for the file whose path
            should be returned.
        :rtype: PathPointer
        """
        return self._root.join(fileid)

    def abspaths(self, fileids=None, include_encoding=False,
                 include_fileid=False):
        """
        Return a list of the absolute paths for all fileids in this corpus;
        or for the given list of fileids, if specified.

        :type fileids: None or str or list
        :param fileids: Specifies the set of fileids for which paths should
            be returned.  Can be None, for all fileids; a list of
            file identifiers, for a specified set of fileids; or a single
            file identifier, for a single file.  Note that the return
            value is always a list of paths, even if ``fileids`` is a
            single file identifier.

        :param include_encoding: If true, then return a list of
            ``(path_pointer, encoding)`` tuples.

        :rtype: list(PathPointer)
        """
        if fileids is None:
            fileids = self._fileids
        elif isinstance(fileids, basestring):
            fileids = [fileids]

        paths = [self._root.join(f) for f in fileids]

        if include_encoding and include_fileid:
            return zip(paths, [self.encoding(f) for f in fileids], fileids)
        elif include_fileid:
            return zip(paths, fileids)
        elif include_encoding:
            return zip(paths, [self.encoding(f) for f in fileids])
        else:
            return paths

    def open(self, file, sourced=False):
        """
        Return an open stream that can be used to read the given file.
        If the file's encoding is not None, then the stream will
        automatically decode the file's contents into unicode.

        :param file: The file identifier of the file to read.
        """
        encoding = self.encoding(file)
        stream = self._root.join(file).open(encoding)
        if sourced:
            stream = SourcedStringStream(stream, file)
        return stream

    def encoding(self, file):
        """
        Return the unicode encoding for the given corpus file, if known.
        If the encoding is unknown, or if the given file should be
        processed using byte strings (str), then return None.
        """
        if isinstance(self._encoding, dict):
            return self._encoding.get(file)
        else:
            return self._encoding

    def _get_root(self): return self._root
    root = property(_get_root, doc="""
        The directory where this corpus is stored.

        :type: PathPointer""")


######################################################################
#{ Corpora containing categorized items
######################################################################

class CategorizedCorpusReader(object):
    """
    A mixin class used to aid in the implementation of corpus readers
    for categorized corpora.  This class defines the method
    ``categories()``, which returns a list of the categories for the
    corpus or for a specified set of fileids; and overrides ``fileids()``
    to take a ``categories`` argument, restricting the set of fileids to
    be returned.

    Subclasses are expected to:

      - Call ``__init__()`` to set up the mapping.

      - Override all view methods to accept a ``categories`` parameter,
        which can be used *instead* of the ``fileids`` parameter, to
        select which fileids should be included in the returned view.
    """

    def __init__(self, kwargs):
        """
        Initialize this mapping based on keyword arguments, as
        follows:

          - cat_pattern: A regular expression pattern used to find the
            category for each file identifier.  The pattern will be
            applied to each file identifier, and the first matching
            group will be used as the category label for that file.

          - cat_map: A dictionary, mapping from file identifiers to
            category labels.

          - cat_file: The name of a file that contains the mapping
            from file identifiers to categories.  The argument
            ``cat_delimiter`` can be used to specify a delimiter.

        The corresponding argument will be deleted from ``kwargs``.  If
        more than one argument is specified, an exception will be
        raised.
        """
        self._f2c = None #: file-to-category mapping
        self._c2f = None #: category-to-file mapping

        self._pattern = None #: regexp specifying the mapping
        self._map = None #: dict specifying the mapping
        self._file = None #: fileid of file containing the mapping
        self._delimiter = None #: delimiter for ``self._file``

        if 'cat_pattern' in kwargs:
            self._pattern = kwargs['cat_pattern']
            del kwargs['cat_pattern']
        elif 'cat_map' in kwargs:
            self._map = kwargs['cat_map']
            del kwargs['cat_map']
        elif 'cat_file' in kwargs:
            self._file = kwargs['cat_file']
            del kwargs['cat_file']
            if 'cat_delimiter' in kwargs:
                self._delimiter = kwargs['cat_delimiter']
                del kwargs['cat_delimiter']
        else:
            raise ValueError('Expected keyword argument cat_pattern or '
                             'cat_map or cat_file.')


        if ('cat_pattern' in kwargs or 'cat_map' in kwargs or
            'cat_file' in kwargs):
            raise ValueError('Specify exactly one of: cat_pattern, '
                             'cat_map, cat_file.')

    def _init(self):
        self._f2c = defaultdict(set)
        self._c2f = defaultdict(set)

        if self._pattern is not None:
            for file_id in self._fileids:
                category = re.match(self._pattern, file_id).group(1)
                self._add(file_id, category)

        elif self._map is not None:
            for (file_id, categories) in self._map.items():
                for category in categories:
                    self._add(file_id, category)

        elif self._file is not None:
            for line in self.open(self._file).readlines():
                line = line.strip()
                file_id, categories = line.split(self._delimiter, 1)
                if file_id not in self.fileids():
                    raise ValueError('In category mapping file %s: %s '
                                     'not found' % (self._file, file_id))
                for category in categories.split(self._delimiter):
                    self._add(file_id, category)

    def _add(self, file_id, category):
        self._f2c[file_id].add(category)
        self._c2f[category].add(file_id)

    def categories(self, fileids=None):
        """
        Return a list of the categories that are defined for this corpus,
        or for the file(s) if it is given.
        """
        if self._f2c is None:
            self._init()
        if fileids is None:
            return sorted(self._c2f)
        if isinstance(fileids, basestring):
            fileids = [fileids]
        return sorted(set.union(*[self._f2c[d] for d in fileids]))

    def fileids(self, categories=None):
        """
        Return a list of file identifiers for the files that make up
        this corpus, or that make up the given category(s) if specified.
        """
        if categories is None:
            return super(CategorizedCorpusReader, self).fileids()
        elif isinstance(categories, basestring):
            if self._f2c is None:
                self._init()
            if categories in self._c2f:
                return sorted(self._c2f[categories])
            else:
                raise ValueError('Category %s not found' % categories)
        else:
            if self._f2c is None:
                self._init()
            return sorted(set.union(*[self._c2f[c] for c in categories]))

######################################################################
#{ Treebank readers
######################################################################

#[xx] is it worth it to factor this out?
class SyntaxCorpusReader(CorpusReader):
    """
    An abstract base class for reading corpora consisting of
    syntactically parsed text.  Subclasses should define:

      - ``__init__``, which specifies the location of the corpus
        and a method for detecting the sentence blocks in corpus files.
      - ``_read_block``, which reads a block from the input stream.
      - ``_word``, which takes a block and returns a list of list of words.
      - ``_tag``, which takes a block and returns a list of list of tagged
        words.
      - ``_parse``, which takes a block and returns a list of parsed
        sentences.
    """
    def _parse(self, s):
        raise NotImplementedError()
    def _word(self, s):
        raise NotImplementedError()
    def _tag(self, s):
        raise NotImplementedError()
    def _read_block(self, stream):
        raise NotImplementedError()

    def raw(self, fileids=None):
        if fileids is None: fileids = self._fileids
        elif isinstance(fileids, basestring): fileids = [fileids]
        return concat([self.open(f).read() for f in fileids])

    def parsed_sents(self, fileids=None):
        reader = self._read_parsed_sent_block
        return concat([StreamBackedCorpusView(fileid, reader, encoding=enc)
                       for fileid, enc in self.abspaths(fileids, True)])

    def tagged_sents(self, fileids=None, simplify_tags=False):
        def reader(stream):
            return self._read_tagged_sent_block(stream, simplify_tags)
        return concat([StreamBackedCorpusView(fileid, reader, encoding=enc)
                       for fileid, enc in self.abspaths(fileids, True)])

    def sents(self, fileids=None):
        reader = self._read_sent_block
        return concat([StreamBackedCorpusView(fileid, reader, encoding=enc)
                       for fileid, enc in self.abspaths(fileids, True)])

    def tagged_words(self, fileids=None, simplify_tags=False):
        def reader(stream):
            return self._read_tagged_word_block(stream, simplify_tags)
        return concat([StreamBackedCorpusView(fileid, reader, encoding=enc)
                       for fileid, enc in self.abspaths(fileids, True)])

    def words(self, fileids=None):
        return concat([StreamBackedCorpusView(fileid,
                                              self._read_word_block,
                                              encoding=enc)
                       for fileid, enc in self.abspaths(fileids, True)])

    #------------------------------------------------------------
    #{ Block Readers

    def _read_word_block(self, stream):
        return sum(self._read_sent_block(stream), [])

    def _read_tagged_word_block(self, stream, simplify_tags=False):
        return sum(self._read_tagged_sent_block(stream, simplify_tags), [])

    def _read_sent_block(self, stream):
        return filter(None, [self._word(t) for t in self._read_block(stream)])

    def _read_tagged_sent_block(self, stream, simplify_tags=False):
        return filter(None, [self._tag(t, simplify_tags)
                             for t in self._read_block(stream)])

    def _read_parsed_sent_block(self, stream):
        return filter(None, [self._parse(t) for t in self._read_block(stream)])

    #} End of Block Readers
    #------------------------------------------------------------

