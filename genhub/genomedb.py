#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2015   Daniel Standage <daniel.standage@gmail.com>
# Copyright (c) 2015   Indiana University
#
# This file is part of genhub (http://github.com/standage/genhub) and is
# licensed under the BSD 3-clause license: see LICENSE.txt.
# -----------------------------------------------------------------------------

"""
Class for managing a genome database.

By "genome database" we mean a collection of sequence, annotation, and
ancillary data files for a annotated genome assembly.

This "superclass" defines many default characteristics and behaviors that are
shared across different genome databases. Subclasses implement additional
specifics for managing data from a particular source.
"""

from __future__ import print_function
import gzip
import hashlib
import os
import subprocess
import sys
import tempfile
import genhub
try:
    FileNotFoundError
except NameError:  # pragma: no cover
    FileNotFoundError = IOError


class GenomeDB(object):

    def __init__(self, label, conf, workdir='.'):
        self.label = label
        self.config = conf
        self.workdir = workdir
        assert 'source' in conf, 'data source unconfigured'

    # ----------
    # Filenames for unprocessed data from the primary source.
    # ----------

    def file_path(self, filename, check=False, message=None):
        """
        Resolve a file's complete path, optionally checking if the file exists.
        """
        filepath = '%s/%s/%s' % (self.workdir, self.label, filename)
        if check:  # pragma: no cover
            if not os.path.exists(filepath):
                msg = 'file "%s" not found' % filepath
                if message is not None:
                    msg += '; %s' % message
                raise FileNotFoundError(msg)
        return filepath

    @property
    def gdnafilename(self):
        if 'scaffolds' in self.config:
            return self.config['scaffolds']
        return None  # pragma: no cover

    @property
    def gff3filename(self):
        return self.config['annotation']

    @property
    def protfilename(self):
        if 'proteins' in self.config:
            return self.config['proteins']
        return 'protein.fa.gz'

    # ----------
    # Complete file paths for unprocessed data.
    # ----------

    @property
    def gdnapath(self):
        return self.file_path(self.gdnafilename)

    @property
    def gff3path(self):
        return self.file_path(self.gff3filename)

    @property
    def protpath(self):
        return self.file_path(self.protfilename)

    # ----------
    # File paths for processed data.
    # ----------

    @property
    def gdnafile(self):
        filename = '%s.gdna.fa' % self.label
        return self.file_path(filename)

    @property
    def gff3file(self):
        filename = '%s.gff3' % self.label
        return self.file_path(filename)

    @property
    def protfile(self):
        filename = '%s.all.prot.fa' % self.label
        return self.file_path(filename)

    # ----------
    # Determine whether raw data files need to be compressed during download.
    # ----------

    @property
    def compress_gdna(self):
        if 'compress' in self.config and 'gdna' in self.config['compress']:
            return True
        return False

    @property
    def compress_gff3(self):
        if 'compress' in self.config and 'gff3' in self.config['compress']:
            return True
        return False

    @property
    def compress_prot(self):
        if 'compress' in self.config and 'prot' in self.config['compress']:
            return True
        return False

    # ----------
    # Miscellaneous properties.
    # ----------

    @property
    def source(self):
        """The institutional source of the data."""
        return self.config['source']

    @property
    def dbdir(self):
        """Dedicated directory for this genome database."""
        return '%s/%s' % (self.workdir, self.label)

    # ----------
    # Build task method implementations.
    # ----------

    def download_gdna(self, logstream=sys.stderr):  # pragma: no cover
        """Download genomic DNA sequence."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download genome sequence from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.gdnaurl, self.gdnapath,
                                     compress=self.compress_gdna)

    def download_gff3(self, logstream=sys.stderr):  # pragma: no cover
        """Download genome annotation."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download genome annotation from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.gff3url, self.gff3path,
                                     compress=self.compress_gff3)

    def download_prot(self, logstream=sys.stderr):  # pragma: no cover
        """Download protein sequences."""
        subprocess.call(['mkdir', '-p', self.dbdir])
        if logstream is not None:
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'download protein sequences from %r' % self
            print(logmsg, file=logstream)
        genhub.download.url_download(self.proturl, self.protpath,
                                     compress=self.compress_prot)

    def download(self, logstream=sys.stderr):  # pragma: no cover
        """Run download task."""
        self.download_gdna(logstream)
        self.download_gff3(logstream)
        self.download_prot(logstream)

    def format(self, logstream=sys.stderr, verify=True):  # pragma: no cover
        """Run format task"""
        self.preprocess_gdna(logstream=logstream, verify=verify)
        self.preprocess_gff3(logstream=logstream, verify=verify)
        self.preprocess_prot(logstream=logstream, verify=verify)

    def preprocess(self, datatype, logstream=sys.stderr, verify=True):
        """
        Preprocess genome data files.

        To read from or write to a custom input/output streams (rather than the
        default file locations), set `instream` and/or `outstream` to a
        readable or writeable file handle, a stringio, or similar object.

        Note that this is a wrapper function: each subclass must implement 3
        methods (`format_gdna`, `format_gff3`, and `format_prot`) to do the
        actual formatting.
        """
        datatypes = {'gdna': 'genome sequence file',
                     'gff3': 'annotation file',
                     'prot': 'protein sequence file'}
        assert datatype in datatypes

        if logstream is not None:  # pragma: no cover
            logmsg = '[GenHub: %s] ' % self.config['species']
            logmsg += 'preprocess %s' % datatypes[datatype]
            print(logmsg, file=logstream)

        infile = {'gdna': self.gdnapath,
                  'gff3': self.gff3path,
                  'prot': self.protpath}[datatype]
        outfile = {'gdna': self.gdnafile,
                   'gff3': self.gff3file,
                   'prot': self.protfile}[datatype]
        if datatype != 'gff3':
            if infile.endswith('.gz'):
                instream = gzip.open(infile, 'rt')
            else:
                instream = open(infile, 'r')
            outstream = open(outfile, 'w')

        if datatype == 'gdna':
            self.format_gdna(instream, outstream, logstream)
        elif datatype == 'prot':
            self.format_prot(instream, outstream, logstream)
        else:
            self.format_gff3(logstream)

        if datatype != 'gff3':
            instream.close()
            outstream.close()

        if verify is False:
            return

        if 'checksums' in self.config and datatype in self.config['checksums']:
            sha1 = self.config['checksums'][datatype]
            testsha1 = self.file_sha1(outfile)
            assert testsha1 == sha1, ('%s %s integrity check failed\n%s\n%s' %
                                      (self.label, datatypes[datatype],
                                       testsha1, sha1))
        else:  # pragma: no cover
            message = 'Cannot verify integrity of %s ' % self.label
            message += '%s without a checksum' % datatypes[datatype]
            print(message, file=logstream)

    def preprocess_gdna(self, logstream=sys.stderr, verify=True):
        self.preprocess('gdna', logstream, verify)

    def preprocess_gff3(self, logstream=sys.stderr, verify=True):
        self.preprocess('gff3', logstream, verify)

    def preprocess_prot(self, logstream=sys.stderr, verify=True):
        self.preprocess('prot', logstream, verify)

    def filter_file(self):
        """
        Write exclusion filter to a temporary file and return.

        Data configurations may include an optional `annotfilter` with patterns
        to discard from the input annotation a la `grep -v`. This function
        retrieves the pattern(s) from the genome configuration and writes them
        to a temporary file that can be used in a `grep -vf` command. The
        calling function is responsible for unlinking the temporary file from
        the operating system.
        """
        if 'annotfilter' not in self.config:
            return None
        excludefile = tempfile.NamedTemporaryFile(mode='wt', delete=False)
        if isinstance(self.config['annotfilter'], str):
            print(self.config['annotfilter'], file=excludefile)
        else:
            for exclusion in self.config['annotfilter']:
                print(exclusion, file=excludefile)
        excludefile.close()
        return excludefile

    def file_sha1(self, filepath):
        """
        Stolen shamelessly from http://stackoverflow.com/a/19711609/459780.
        """
        sha = hashlib.sha1()
        with open(filepath, 'rb') as f:
            while True:
                block = f.read(2**10)
                if not block:
                    break
                sha.update(block)
            return sha.hexdigest()


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------

def test_file_path():
    """GenomeDB File name resolution"""
    config = genhub.test_registry.genome('Bimp')
    db = GenomeDB('Bimp', config)
    assert db.file_path('bogus.txt') == './Bimp/bogus.txt'
    db = GenomeDB('Bimp', config, 'wd')
    assert db.file_path('Bimp.gff3') == 'wd/Bimp/Bimp.gff3'
    checkfailed = False
    try:
        config = genhub.test_registry.genome('Amel')
        db = GenomeDB('Amel', config)
        path = db.file_path('Amel.iloci.gff3', check=True)
    except FileNotFoundError as e:
        checkfailed = True
        assert e.args[0] == 'file "./Amel/Amel.iloci.gff3" not found'
    assert checkfailed


def test_props():
    """GenomeDB properties"""
    config = genhub.test_registry.genome('Bimp')
    db = GenomeDB('Bimp', config)
    assert db.dbdir == './Bimp'
    assert db.gdnafile == './Bimp/Bimp.gdna.fa'
    assert db.gff3file == './Bimp/Bimp.gff3'
    assert db.protfile == './Bimp/Bimp.all.prot.fa'
    assert db.source == 'refseq'

    config = genhub.test_registry.genome('Dqua')
    db = GenomeDB('Dqua', config, workdir='/opt/data/genomes')
    assert db.dbdir == '/opt/data/genomes/Dqua'
    assert db.gdnafile == '/opt/data/genomes/Dqua/Dqua.gdna.fa'
    assert db.gff3file == '/opt/data/genomes/Dqua/Dqua.gff3'
    assert db.protfile == '/opt/data/genomes/Dqua/Dqua.all.prot.fa'
    assert db.source == 'crg'


def test_filter_file():
    """GenomeDB filter file"""
    config = genhub.test_registry.genome('Lalb')
    db = GenomeDB('Lalb', config)
    assert db.filter_file() is None

    config = genhub.test_registry.genome('Drer')
    db = GenomeDB('Drer', config)
    ff = db.filter_file()
    with open(ff.name, 'r') as infile:
        excludestr = infile.read()
        assert excludestr.strip() == 'NC_002333.2'
    os.unlink(ff.name)
