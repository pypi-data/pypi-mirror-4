#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This module provides tools to administrate sources.
"""

from __future__ import with_statement

import os
import os.path as op
from textwrap import dedent
from urllib import urlretrieve
from zipfile import ZipFile
import shutil
from shutil import copy

# Not in standard library
import yaml

# Relative paths handling
DIRNAME = op.dirname(__file__)

def relative(rel_path, root=DIRNAME):
    """Handle relative paths.
    """
    return op.join(op.realpath(root), rel_path)


# 1) Path to global configuration
# 2) Root folder where we find data
# 3) Cache directory
UPDATE_SCRIPT_PATH  = relative('DataSources/CheckDataUpdates.sh')
SOURCES_CONF_PATH   = relative('DataSources/Sources.yaml')
SOURCES_DIR         = op.dirname(SOURCES_CONF_PATH)
CACHE_DIR           = op.join(os.getenv('HOME', '.'), '.GeoBases.d')

if not op.isdir(CACHE_DIR):
    os.mkdir(CACHE_DIR)

# Poorly documented paths are relative from the sources dir
DEFAULT_IS_RELATIVE = True

# We only export the main class
__all__ = ['SourcesManager', 'is_remote', 'is_archive']


class SourcesManager(object):
    """
    This class is used to administrate sources.
    """
    def __init__(self,
                 sources_conf_path_origin=SOURCES_CONF_PATH,
                 sources_dir=SOURCES_DIR,
                 cache_dir=CACHE_DIR,
                 update_script_path=UPDATE_SCRIPT_PATH,
                 override=False):

        # Path to the configuration file origin file
        self.sources_conf_path_origin = sources_conf_path_origin

        # Creating use space file
        self.sources_conf_path = op.join(cache_dir,
                                         op.basename(self.sources_conf_path_origin))

        # We copy in user space the origin conf file
        if not op.isfile(self.sources_conf_path) or override is True:
            try:
                copy(self.sources_conf_path_origin,
                     self.sources_conf_path)

            except shutil.Error:
                # Copy did not happen because the two files are the same
                print 'Did not copy %s to %s' % (self.sources_conf_path_origin, 
                                                 self.sources_conf_path)
                # We will use the origin file
                self.sources_conf_path = self.sources_conf_path_origin


        # Root folder where we find data
        self.sources_dir = sources_dir

        # Cache directory
        self.cache_dir = cache_dir

        # Maintenance script
        self.update_script_path = update_script_path

        # Loading data
        self.sources = None
        self.load()



    def load(self):
        """Load configuration file.
        """
        with open(self.sources_conf_path) as fl:
            self.sources = yaml.load(fl)


    def __contains__(self, source):
        """For *in* test.
        """
        return source in self.sources


    def __iter__(self):
        """For iteration.
        """
        return iter(self.sources)


    def check_data_updates(self, force=False):
        """Launch update script on data files.
        """
        force_option = '-f' if force else ''

        os.system('bash %s %s' % (self.update_script_path, force_option))


    def get(self, source=None):
        """Get source information.
        """
        if source is None:
            return self.sources

        if source not in self.sources:
            raise KeyError('Source %s not in sources.' % source)

        return self.sources[source]


    def add(self, source, config=None):
        """Add new source.
        """
        if source in self.sources:
            print 'Source "%s" already exists.' % source
            return

        if config is None:
            self.sources[source] = {}
        else:
            self.sources[source] = config


    def is_in_cache(self, filename):
        """Is filename already in cache?
        """
        return op.isfile(op.join(self.cache_dir, filename))


    def is_path_from_cache(self, path):
        """Is a path from the cache?.
        """
        return path == op.join(self.cache_dir, op.basename(path))


    def copy_to_cache(self, path):
        """Move source file in cache directory.
        """
        if not op.isfile(path):
            print 'File %s does not exist' % path
            return False, None

        try:
            copy(path, self.cache_dir)
        except shutil.Error:
            # Copy did not happen because the two files are the same
            return False, path
        else:
            return True, op.join(self.cache_dir, op.basename(path))


    def drop(self, source=None):
        """Drop source.
        """
        if source is None:
            self.sources = {}

        if source not in self.sources:
            print 'Source "%s" does not exist.' % source
            return

        del self.sources[source]


    def update(self, source, config):
        """Update source.
        """
        if source not in self.sources:
            print 'Source "%s" not in sources.' % source
            return

        for option, option_config in config.iteritems():
            self.sources[source][option] = option_config


    @staticmethod
    def convert(obj):
        """YAML formatting.
        """
        return yaml.safe_dump(obj,
                              indent=4,
                              default_flow_style=False)


    def full_status(self, source=None):
        """Show source full status.
        """
        if source is None:
            print self.convert(self.sources)
            return

        if source not in self.sources:
            print 'Source %s not in sources.' % source
            return

        print self.convert({
            source : self.get(source)
        })


    def save(self, filename=None):
        """Dump sources in configuration file.
        """
        if filename is None:
            filename = self.sources_conf_path

        with open(filename, 'w') as f:
            f.write(self.convert(self.sources))


    def restore(self, load=False):
        """Restore original file.
        """
        try:
            copy(self.sources_conf_path_origin,
                 self.sources_conf_path)

        except shutil.Error:
            # Copy did not happen because the two files are the same
            print 'Did not copy %s to %s' % (self.sources_conf_path_origin,
                                             self.sources_conf_path)

        if load:
            self.load()


    def build_status(self, source=None):
        """Display informations on available sources.
        """
        if source is None:
            displayed = sorted(self.sources)
        else:
            if source not in self.sources:
                return 'Source "%s" not in sources.' % source
            displayed = [source]

        missing = '<none>'

        def fmt_keys(l):
            """Nice key_fields formatting."""
            if l is None:
                return missing
            if isinstance(l, (list, tuple, set)):
                return '+'.join(l)
            return str(l)

        def fmt_path(p):
            """Nice path formatting."""
            if isinstance(p, str):
                return str(p)
            if not is_archive(p):
                return p['file']
            return '%s -> %s' % (p['file'], p['extract'])

        tip = [dedent('''
        * Data sources  from %s
        * Configuration from %s
        ''' % (self.sources_dir, self.sources_conf_path))]

        tip.append('-' * 80)
        tip.append('%-20s | %-25s | %s' % ('NAME', 'KEY', 'PATHS (DEFAULT + FAILOVERS)'))
        tip.append('-' * 80)

        for source in displayed:
            config = self.sources[source]

            if config is not None:
                keys  = config.get('key_fields', missing)
                paths = config.get('paths', missing)
                if not paths:
                    paths = missing
            else:
                keys, paths = missing, missing

            if isinstance(paths, (str, dict)):
                paths = [paths]
            tip.append('%-20s | %-25s | %s' % \
                       (source, fmt_keys(keys), '.) %s' % fmt_path(paths[0])))

            for n, path in enumerate(paths[1:], start=1):
                tip.append('%-20s | %-25s | %s' % \
                           ('-', '-', '%s) %s' % (n, fmt_path(path))))

        tip.append('-' * 80)

        return '\n'.join(tip)


    def help_permanent_add(self, options):
        """Display help on how to make a data source permanent.
        """
        conf = {
            'paths' : {
                'file'  : '<INSERT_ABSOLUTE_FILE_PATH>',
                'local' : False,
            }
        }

        for option, value in options.iteritems():
            # Source is not allowed in configuration, replaced by paths
            if option not in ('source', 'verbose'):
                conf[option] = value

        print
        print '* You can make this data source permanent!'
        print '* Edit %s with:' % self.sources_conf_path
        print
        print '$ cat >> %s << EOF' % self.sources_conf_path
        print '# ================ BEGIN ==============='
        print
        print self.convert({
            '<INSERT_ANY_NAME>' : conf
        })

        print '# ================  END  ==============='
        print 'EOF'
        print
        print '* Replace the placeholders <INSERT_...> with:'
        print '$ vim %s' % self.sources_conf_path
        print


    def handle_path(self, path, verbose):
        """
        Handle file downloading/uncompressing and returns
        path to file to be opened.
        """
        if not is_remote(path):
            file_ = path['file']
        else:
            file_, success = download_lazy(path['file'], self.cache_dir, verbose)

            if not success:
                if verbose:
                    print '/!\ Failed to download "%s".' % path['file']
                return

        if is_archive(path):
            archive = file_
            file_, success = extract_lazy(archive, path['extract'], self.cache_dir, verbose)

            if not success:
                if verbose:
                    print '/!\ Failed to extract "%s" from "%s".' % \
                            (path['extract'], archive)
                return

        return file_


    def convert_paths_format(self, paths, default_is_relative=DEFAULT_IS_RELATIVE):
        """Convert all paths to the same format.
        """
        if paths is None:
            return

        # If paths is just *one* archive or *one* file
        if isinstance(paths, (str, dict)):
            paths = [paths]

        # We normalize all path as a dict structure
        new_paths = []

        for path in paths:
            if isinstance(path, str):
                path = {
                    'file' : path,
                }

            # We append a copy
            new_paths.append(dict(path.items()))


        for npath in new_paths:
            # 'local' is only used for sources from configuration
            # to have a relative path from the configuration file
            if 'local' not in npath:
                npath['local'] = default_is_relative

            if is_remote(npath):
                npath['local'] = False

            if not is_remote(npath) and npath['local'] is True:
                npath['file'] = op.join(op.realpath(self.sources_dir), npath['file'])

        return tuple(new_paths)




# Remote prefix detection
R_PREFIXES = set(['http://', 'https://'])
has_prefix = lambda path, prefixes: any(path.lower().startswith(p) for p in prefixes)

def is_remote(path):
    """Tells if a path is remote.
    """
    return has_prefix(path['file'], R_PREFIXES)

# Remote prefix detection
is_archive = lambda path: 'extract' in path

# Date comparisons
def is_older(a, b):
    """Test file last modifcation time.
    """
    try:
        if os.stat(a).st_mtime < os.stat(b).st_mtime:
            return True
    except OSError:
        # If this fails, we say it is not older
        pass
    return False


def download_lazy(resource, cache_dir, verbose=True):
    """
    Download a remote file only if target file is not already
    in cache directory.
    Returns boolean for success or failure, and path
    to downloaded file (may not be exactly the same as the one checked).
    """
    # If in cache directory, we use it, otherwise we download it
    filename_test = op.join(cache_dir, op.basename(resource))

    if op.isfile(filename_test):
        if verbose:
            print '/!\ Using "%s" already in cache directory for "%s"' % \
                    (filename_test, resource)
        return filename_test, True

    if verbose:
        print '/!\ Downloading "%s" in cache directory from "%s"' % \
                (filename_test, resource)
    try:
        dl_filename, _ = urlretrieve(resource, filename_test)
    except IOError:
        return None, False
    else:
        return dl_filename, True


def extract_lazy(archive, filename, cache_dir, verbose=True):
    """
    Extract a file from archive if file is not already in
    the cache directory.
    """
    # Perhaps the file was already extracted here
    # We also check the dates of modification in case
    # the extracted file obsolete
    filename_test = op.join(cache_dir, filename)

    if op.isfile(filename_test):
        if is_older(archive, filename_test):
            if verbose:
                print '/!\ Skipping extraction for "%s", already at "%s"' % \
                        (filename, filename_test)
            return filename_test, True

        if verbose:
            print '/!\ File "%s" already at "%s", but "%s" is newer, removing' % \
                    (filename, filename_test, archive)

    if verbose:
        print '/!\ Extracting "%s" from "%s" in "%s"' % \
                (filename, archive, filename_test)

    # We extract one file from the archive
    try:
        extracted = ZipFile(archive).extract(filename, op.dirname(filename_test))
    except IOError:
        return None, False
    except KeyError:
        if verbose:
            print '/!\ "%s" not in "%s"' % (filename, archive)
        return None, False
    else:
        return extracted, True




def _test():
    """When called directly, launching doctests.
    """
    import doctest

    opt =  (doctest.ELLIPSIS |
            doctest.NORMALIZE_WHITESPACE)
            #doctest.REPORT_ONLY_FIRST_FAILURE)
            #doctest.IGNORE_EXCEPTION_DETAIL)

    doctest.testmod(optionflags=opt)



if __name__ == '__main__':
    _test()

