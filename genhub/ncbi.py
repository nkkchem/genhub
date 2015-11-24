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
Module for handling NCBI data.

Utilities for downloading genome assemblies, annotations, and protein
sequences from NCBI's FTP site.
"""

from __future__ import print_function
import gzip
import subprocess
import sys
import yaml
import genhub


class NcbiGenomeDB(genhub.genomedb.GenomeDB):

    def __init__(self, label, conf, workdir='.'):
        super(NcbiGenomeDB, self).__init__(label, conf, workdir)
        assert self.config['source'] == 'ncbi'
        assert 'species' in self.config
        species = self.config['species'].replace(' ', '_')
        self.specbase = 'ftp://ftp.ncbi.nih.gov/genomes/%s' % species

    def __repr__(self):
        return 'NCBI'

    @property
    def moltype(self):
        chrmtype = 'chromosomes' in self.config
        scaftype = 'scaffolds' in self.config
        assert chrmtype != scaftype, ('Must configure only chromosomes or '
                                      'scaffolds, not both')
        if chrmtype:
            return 'chromosomes'
        return 'scaffolds'

    @property
    def gdnafilename(self):
        if self.moltype == 'scaffolds':
            return self.config['scaffolds']
        else:
            return '%s.orig.fa.gz' % (self.label)

    @property
    def gff3filename(self):
        return self.config['annotation']

    @property
    def protfilename(self):
        return 'protein.fa.gz'

    @property
    def gdnapath(self):
        return genhub.file_path(self.gdnafilename, self.label, self.workdir)

    @property
    def gff3path(self):
        return genhub.file_path(self.gff3filename, self.label, self.workdir)

    @property
    def protpath(self):
        return genhub.file_path(self.protfilename, self.label, self.workdir)

    @property
    def gdnaurl(self):
        if self.moltype == 'scaffolds':
            return '%s/CHR_Un/%s' % (self.specbase, self.gdnafilename)
        else:
            urls = list()
            prefix = self.config['prefix']
            for chrmfile in self.config['chromosomes']:
                url = '%s/%s/%s' % (self.specbase, prefix, chrmfile)
                urls.append(url)
            return urls

    @property
    def gff3url(self):
        return '%s/GFF/%s' % (self.specbase, self.config['annotation'])

    @property
    def proturl(self):
        return '%s/protein/protein.fa.gz' % self.specbase


# -----------------------------------------------------------------------------
# Unit tests
# -----------------------------------------------------------------------------


def test_scaffolds():
    """NCBI scaffolds download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/CHR_Un/'
               'emon_ref_3.4_chrUn.fa.gz')
    testpath = './Emon/emon_ref_3.4_chrUn.fa.gz'
    emon_db = NcbiGenomeDB(label, config)
    assert emon_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (emon_db.gdnaurl, testurl)
    assert emon_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (emon_db.gdnapath, testpath)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/CHR_Un/'
               'bv_ref_1.1_chrUn.fa.gz')
    testpath = '/some/path/Bvul/bv_ref_1.1_chrUn.fa.gz'
    bvul_db = NcbiGenomeDB(label, config, workdir='/some/path')
    assert bvul_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (bvul_db.gdnaurl, testurl)
    assert bvul_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (bvul_db.gdnapath, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/CHR_Un/'
               'ado_ref_Apis_dorsata_1.3_chrUn.fa.gz')
    testpath = './Ador/ado_ref_Apis_dorsata_1.3_chrUn.fa.gz'
    ador_db = NcbiGenomeDB(label, config)
    assert '%r' % ador_db == 'NCBI'
    assert ador_db.gdnaurl == testurl, \
        'scaffold URL mismatch\n%s\n%s' % (ador_db.gdnaurl, testurl)
    assert ador_db.gdnapath == testpath, \
        'scaffold path mismatch\n%s\n%s' % (ador_db.gdnapath, testpath)


def test_chromosomes():
    """NCBI chromosome download"""

    label, config = genhub.conf.load_one('conf/test/Docc.yml')
    urls = ['docc_ref_1.6_1.fa.gz', 'docc_ref_1.6_2.fa.gz',
            'docc_ref_1.6_3.fa.gz', 'docc_ref_1.6_4.fa.gz',
            'docc_ref_1.6_5.fa.gz', 'docc_ref_1.6_6.fa.gz',
            'docc_ref_1.6_7.fa.gz', 'docc_ref_1.6_8.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Draconis_occidentalis/'
              'Assembled_chromosomes/seq/')
    testurls = [prefix + x for x in urls]
    testpath = './Docc/Docc.orig.fa.gz'
    docc_db = NcbiGenomeDB(label, config)
    assert docc_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (docc_db.gdnaurl, testurls)
    assert docc_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (docc_db.gdnapath, chrmpath)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    urls = ['epeg_reg_Epe_2.1_01.fa.gz', 'epeg_reg_Epe_2.1_02.fa.gz',
            'epeg_reg_Epe_2.1_03.fa.gz', 'epeg_reg_Epe_2.1_04.fa.gz',
            'epeg_reg_Epe_2.1_05.fa.gz', 'epeg_reg_Epe_2.1_06.fa.gz',
            'epeg_reg_Epe_2.1_07.fa.gz', 'epeg_reg_Epe_2.1_08.fa.gz',
            'epeg_reg_Epe_2.1_09.fa.gz', 'epeg_reg_Epe_2.1_10.fa.gz',
            'epeg_reg_Epe_2.1_11.fa.gz', 'epeg_reg_Epe_2.1_12.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/'
              'Assembled_chromosomes/seq/')
    testurls = [prefix + x for x in urls]
    testpath = './Epeg/Epeg.orig.fa.gz'
    epeg_db = NcbiGenomeDB(label, config)
    assert epeg_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (epeg_db.gdnaurl, testurls)
    assert epeg_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (epeg_db.gdnapath, chrmpath)

    label, config = genhub.conf.load_one('conf/HymHub/Amel.yml')
    urls = ['ame_ref_Amel_4.5_unplaced.fa.gz', 'ame_ref_Amel_4.5_chrLG1.fa.gz',
            'ame_ref_Amel_4.5_chrLG2.fa.gz', 'ame_ref_Amel_4.5_chrLG3.fa.gz',
            'ame_ref_Amel_4.5_chrLG4.fa.gz', 'ame_ref_Amel_4.5_chrLG5.fa.gz',
            'ame_ref_Amel_4.5_chrLG6.fa.gz', 'ame_ref_Amel_4.5_chrLG7.fa.gz',
            'ame_ref_Amel_4.5_chrLG8.fa.gz', 'ame_ref_Amel_4.5_chrLG9.fa.gz',
            'ame_ref_Amel_4.5_chrLG10.fa.gz', 'ame_ref_Amel_4.5_chrLG11.fa.gz',
            'ame_ref_Amel_4.5_chrLG12.fa.gz', 'ame_ref_Amel_4.5_chrLG13.fa.gz',
            'ame_ref_Amel_4.5_chrLG14.fa.gz', 'ame_ref_Amel_4.5_chrLG15.fa.gz',
            'ame_ref_Amel_4.5_chrLG16.fa.gz']
    prefix = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_mellifera/'
              'Assembled_chromosomes/seq/')
    testurls = [prefix + x for x in urls]
    testpath = '/home/student/data/Amel/Amel.orig.fa.gz'
    amel_db = NcbiGenomeDB(label, config, workdir='/home/student/data')
    assert amel_db.gdnaurl == testurls, \
        'chromosome URL mismatch\n%s\n%s' % (amel_db.gdnaurl, testurls)
    assert amel_db.gdnapath == testpath, \
        'chromosome path mismatch\n%s\n%s' % (amel_db.gdnapath, chrmpath)


def test_annot():
    """NCBI annotation download"""

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/GFF/'
               'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    testpath = ('/another/path//Bvul/'
                'ref_Basiliscus_vulgaris_1.1_top_level.gff3.gz')
    bvul_db = NcbiGenomeDB(label, config, workdir='/another/path/')
    assert bvul_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (bvul_db.gff3url, testurl)
    assert bvul_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (bvul_db.gff3path, testpath)

    label, config = genhub.conf.load_one('conf/test/Epeg.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_pegasus/GFF/'
               'ref_EPEG_2.1_top_level.gff3.gz')
    testpath = './Epeg/ref_EPEG_2.1_top_level.gff3.gz'
    epeg_db = NcbiGenomeDB(label, config)
    assert epeg_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (epeg_db.gff3url, testurl)
    assert epeg_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (epeg_db.gff3path, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/GFF/'
               'ref_Apis_dorsata_1.3_top_level.gff3.gz')
    testpath = './Ador/ref_Apis_dorsata_1.3_top_level.gff3.gz'
    ador_db = NcbiGenomeDB(label, config)
    assert ador_db.gff3url == testurl, \
        'annotation URL mismatch\n%s\n%s' % (ador_db.gff3url, testurl)
    assert ador_db.gff3path == testpath, \
        'annotation path mismatch\n%s\n%s' % (ador_db.gff3path, testpath)


def test_proteins():
    """NCBI protein download"""

    label, config = genhub.conf.load_one('conf/test/Emon.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Equus_monoceros/protein/'
               'protein.fa.gz')
    testpath = './Emon/protein.fa.gz'
    emon_db = NcbiGenomeDB(label, config)
    assert emon_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (emon_db.proturl, testurl)
    assert emon_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (emon_db.protpath, testpath)

    label, config = genhub.conf.load_one('conf/test/Bvul.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Basiliscus_vulgaris/protein/'
               'protein.fa.gz')
    testpath = './Bvul/protein.fa.gz'
    bvul_db = NcbiGenomeDB(label, config)
    assert bvul_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (bvul_db.proturl, testurl)
    assert bvul_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (bvul_db.protpath, testpath)

    label, config = genhub.conf.load_one('conf/HymHub/Ador.yml')
    testurl = ('ftp://ftp.ncbi.nih.gov/genomes/Apis_dorsata/protein/'
               'protein.fa.gz')
    testpath = '/home/gandalf/HymHub/Ador/protein.fa.gz'
    ador_db = NcbiGenomeDB(label, config, workdir='/home/gandalf/HymHub')
    assert ador_db.proturl == testurl, \
        'protein URL mismatch\n%s\n%s' % (ador_db.proturl, testurl)
    assert ador_db.protpath == testpath, \
        'protein path mismatch\n%s\n%s' % (ador_db.protpath, testpath)
