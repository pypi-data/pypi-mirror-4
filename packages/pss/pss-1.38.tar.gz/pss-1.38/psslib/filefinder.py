#-------------------------------------------------------------------------------
# pss: filefinder.py
#
# FileFinder class that finds files recursively according to various rules.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os
import re

from .utils import istextfile


class FileFinder(object):
    def __init__(self,
            roots,
            recurse=True,
            ignore_dirs=[],
            find_only_text_files=False,
            search_extensions=[],
            ignore_extensions=[],
            search_file_patterns=[],
            ignore_file_patterns=[]):
        """ Create a new FileFinder. The parameters are the "search rules"
            that dictate which files are found.

            roots:
                Root files/directories from which the search will start

            recurse:
                Should I recurse into sub-directories?

            ignore_dirs:
                Iterable of directory names that will be ignored during the
                search

            find_only_text_files:
                If True, uses a heuristic to determine which files are text
                and which are binary, and ignores the binary files.
                Warning: this option makes FileFinder actually open the files
                and read a portion from them, so it is quite slow.

            search_extensions:
                If non-empty, only files with extensions listed here will be
                found. If empty, files with all extensions will be found

            ignore_extensions:
                Files with extensions listed here will never be found.
                Overrides "search_*" rules

            search_file_patterns:
                If non-empty, only files with names matching these pattens will
                be found. If empty, no pattern restriction is applied

            ignore_file_patterns:
                Files with names matching these patterns will never be found.
                Overrides "search_*" rules
        """
        # Prepare internal data structures from the parameters
        self.roots = roots
        self.recurse = recurse
        self.search_extensions = set(search_extensions)
        self.ignore_extensions = set(ignore_extensions)

        # Distinguish between dirs (like "foo") and paths (like "foo/bar")
        # to ignore.
        self.ignore_dirs = set()
        self.ignore_paths = set()
        for d in ignore_dirs:
            if os.sep in d:
                self.ignore_paths.add(d)
            else:
                self.ignore_dirs.add(d)

        self.find_only_text_files = find_only_text_files
        self.search_file_patterns = [re.compile(p) for p in search_file_patterns]
        self.ignore_file_patterns = [re.compile(p) for p in ignore_file_patterns]

    def files(self):
        """ Generate files according to the search rules. Yield
            paths to files one by one.
        """
        for root in self.roots:
            if os.path.isfile(root):
                if self._file_is_found(root):
                    yield root
            else: # dir
                for dirpath, subdirs, files in os.walk(root):
                    if self._should_ignore_dir(dirpath):
                        # This dir should be ignored, so remove all its subdirs
                        # from the walk and go to next dir.
                        del subdirs[:]
                        continue
                    for filename in files:
                        fullpath = os.path.join(dirpath, filename)
                        if (    self._file_is_found(fullpath) and
                                os.path.exists(fullpath)):
                            yield fullpath
                    if not self.recurse:
                        break

    def _should_ignore_dir(self, dirpath):
        """ Should the given directory be ignored?
        """
        if os.path.split(dirpath)[1] in self.ignore_dirs:
            return True
        elif len(self.ignore_paths) > 0:
            # If we have paths to ignore, things are more difficult...
            for ignored_path in self.ignore_paths:
                found_i = dirpath.rfind(ignored_path)
                if (    found_i == 0 or (
                        found_i > 0 and dirpath[found_i - 1] == os.sep)):
                    return True
        return False

    def _file_is_found(self, filename):
        """ Should this file be "found" according to the search rules?
        """
        # Tries to eliminate the file by all the given search rules. If the
        # file survives until the end, it's found
        root, ext = os.path.splitext(filename)

        if ext in self.ignore_extensions:
            return False

        if self.search_extensions and ext not in self.search_extensions:
            # If search_extensions is non-empty, only files with extensions
            # listed there can be found
            return False

        if any(ignored_pattern.search(filename) for ignored_pattern in self.ignore_file_patterns):
            return False

        # If search_file_patterns is non-empty, the file has to match at least
        # one of the patterns.
        if (self.search_file_patterns and
            not any(p.search(filename) for p in self.search_file_patterns)
            ):
            return False

        # If find_only_text_files, open the file and try to determine whether
        # it's text or binary.
        if self.find_only_text_files:
            try:
                with open(filename, 'rb') as f:
                    if not istextfile(f):
                        return False
            except OSError:
                # If there's a problem opening or reading the file, we
                # don't need it.
                return False

        return True


if __name__ == '__main__':
    import sys
    ff = FileFinder(sys.argv[1:], ignore_dirs=[], recurse=True)
    print(list(ff.files()))

