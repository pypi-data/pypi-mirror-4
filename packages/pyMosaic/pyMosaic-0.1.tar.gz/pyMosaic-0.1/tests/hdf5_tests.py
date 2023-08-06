# -*- coding: utf-8 -*-

# Tests for module mosaic.hdf5
#
# Written by Konrad Hinsen
#

import copy
import os
import tempfile
import unittest

import numpy as N
import numpy.random as NR
import immutable.np as IN
import h5py

import mosaic.mutable_model
import mosaic.immutable_model
import mosaic.array_model
from mosaic.api import is_valid
from mosaic.hdf5 import HDF5Store


class TestHDF5Store(object):

    @classmethod
    def initialize(cls):
        cls.tempdir = tempfile.mkdtemp()
        cls.filename = os.path.join(cls.tempdir, 'test.h5')

    @classmethod
    def cleanup(cls):
        os.remove(cls.filename)
        os.removedirs(cls.tempdir)

    def __init__(self, mode='r'):
        self.file = h5py.File(self.filename, mode)
        self.store = HDF5Store(self.file)

    def close(self):
        del self.store
        self.file.close()

    def __enter__(self):
        return self.store

    def __exit__(self, type, value, traceback):
        self.close()
        return False


class PeptideTest(object):

    def test_universe(self):
        f = mosaic.array_model.Factory()
        array_universe = f(self.universe)
        self.assertTrue(is_valid(array_universe))
        with TestHDF5Store('w') as store:
            store.store("universe", array_universe)
            self.assertTrue(store.retrieve("universe") is array_universe)
        with TestHDF5Store('r') as store:
            universe = store.retrieve("universe")
        self.assertFalse(universe is array_universe)
        self.assertFalse(universe is self.universe)
        self.assertTrue(universe.is_equivalent(array_universe))
        self.assertTrue(universe.is_equivalent(self.universe))
        self.assertTrue(is_valid(universe))

    def test_configuration(self):
        M = self.M
        conf = M.Configuration(self.universe,
                               IN.array(NR.normal(size=(40,3))),
                               IN.array(10., N.float64))
        self.assertTrue(is_valid(conf))
        with TestHDF5Store('w') as store:
            self.assertRaises(IOError,
                              lambda : store.store("configuration", conf))
            store.store("universe", self.universe)
            store.store("configuration", conf)
            self.assertTrue(store.retrieve("configuration") is conf)
        with TestHDF5Store('r') as store:
            conf_r = store.retrieve("configuration")
        self.assertFalse(conf_r is conf)
        self.assertTrue(conf_r.is_equivalent(conf))
        self.assertTrue(is_valid(conf_r))

    def test_property(self):
        M = self.M
        universe = self.universe
        for p in [M.AtomProperty(universe, "mass", "amu",
                     IN.array(NR.normal(size=(universe.number_of_atoms,)))),
                  M.SiteProperty(universe, "foo", "",
                     IN.array(NR.normal(size=(universe.number_of_sites, 3)))),
                  M.TemplateAtomProperty(universe, "mass", "amu",
                     IN.array(NR.normal(size=(universe.number_of_template_atoms,
                                              1)))),
                  M.TemplateSiteProperty(universe, "foo", "bar",
                     IN.array(NR.normal(size=(universe.number_of_template_sites,
                                              2, 2)))),
                  ]:
            self.assertTrue(is_valid(p))
            with TestHDF5Store('w') as store:
                self.assertRaises(IOError,
                                  lambda: store.store("property", p))
                store.store("universe", universe)
                store.store("property", p)
                self.assertTrue(store.retrieve("property") is p)
            with TestHDF5Store('r') as store:
                p_r = store.retrieve("property")
            self.assertFalse(p_r is p)
            self.assertTrue(p_r.is_equivalent(p))
            self.assertTrue(is_valid(p_r))

    def test_label(self):
        M = self.M
        universe = self.universe
        for l in [M.AtomLabel(universe, "element",
                              tuple(a.name
                                    for f, n in universe.molecules
                                    for _ in range(n)
                                    for a in f.recursive_atom_iterator())),
                  M.TemplateAtomLabel(universe, "element",
                                      tuple(a.name
                                            for f, n in universe.molecules
                                            for a in f.recursive_atom_iterator())),
                  M.SiteLabel(universe, "element",
                              tuple(a.name
                                    for f, n in self.universe.molecules
                                    for _ in range(n)
                                    for a in f.recursive_atom_iterator()
                                    for __ in range(a.number_of_sites))),
                  M.TemplateSiteLabel(universe, "element",
                                      tuple(a.name
                                            for f, n in self.universe.molecules
                                            for a in f.recursive_atom_iterator()
                                            for _ in range(a.number_of_sites))),
                  ]:
            self.assertTrue(is_valid(l))
            with TestHDF5Store('w') as store:
                self.assertRaises(IOError,
                                  lambda: store.store("label", l))
                store.store("universe", universe)
                store.store("label", l)
                self.assertTrue(store.retrieve("label") is l)
            with TestHDF5Store('r') as store:
                l_r = store.retrieve("label")
            self.assertFalse(l_r is l)
            self.assertTrue(l_r.is_equivalent(l))
            self.assertTrue(is_valid(l_r))


class MMPeptideTest(unittest.TestCase,
                    PeptideTest):
    M = mosaic.mutable_model

    def setUp(self):
        TestHDF5Store.initialize()

        M = self.M
        C = M.Element('C')
        H = M.Element('H')
        N = M.Element('N')
        O = M.Element('O')
        peptide_group = M.Fragment('peptide', 'peptide_group',
                                   (),
                                   (M.Atom('CA', C),
                                    M.Atom('HA', H),
                                    M.Atom('H', H),
                                    M.Atom('N', N),
                                    M.Atom('C', C),
                                    M.Atom('O', O)),
                                    (('N', 'H', 'single'),
                                     ('N', 'CA', 'single'),
                                     ('CA', 'HA', 'single'),
                                     ('CA', 'C', 'single'),
                                     ('C', 'O', 'double')))
        ala_sidechain = M.Fragment('sidechain', 'ala_sidechain',
                                   (),
                                   (M.Atom('CB', C),
                                    M.Atom('HB1', H),
                                    M.Atom('HB2', H),
                                    M.Atom('HB3', H)),
                                   (('CB', 'HB1', 'single'),
                                    ('CB', 'HB2', 'single'),
                                    ('CB', 'HB3', 'single'),))
        ala = lambda label: M.Fragment(label, 'alanine',
                                       (copy.copy(peptide_group),
                                        copy.copy(ala_sidechain)),
                                       (),
                                       (('peptide.CA',
                                         'sidechain.CB',
                                         'single'),))
        ala_dipeptide = M.Polymer('di_ala', 'alanine_dipeptide',
                                  (ala('ALA1'), ala('ALA2')),
                                  (('ALA1.peptide.C',
                                    'ALA2.peptide.N',
                                    'single'),),
                                  'polypeptide')
        self.universe = M.Universe('cube', [(ala_dipeptide, 2)],
                                   convention='my_own')
        self.assertTrue(is_valid(self.universe))

    def tearDown(self):
        TestHDF5Store.cleanup()


class IMPeptideTest(unittest.TestCase,
                    PeptideTest):
    M = mosaic.immutable_model

    def setUp(self):
        TestHDF5Store.initialize()

        M = self.M
        C = M.element('C')
        H = M.element('H')
        N = M.element('N')
        O = M.element('O')
        peptide_group = M.fragment('peptide',
                                   (),
                                   (('CA', M.atom(C)),
                                    ('HA', M.atom(H)),
                                    ('H', M.atom(H)),
                                    ('N', M.atom(N)),
                                    ('C', M.atom(C)),
                                    ('O', M.atom(O))),
                                   (('N', 'H', "single"),
                                    ('N', 'CA', "single"),
                                    ('CA', 'HA', "single"),
                                    ('CA', 'C', "single"),
                                    ('C', 'O', "double")))
        ala_sidechain = M.fragment('ala_sidechain',
                                   (),
                                   (('CB', M.atom(C)),
                                    ('HB1', M.atom(H)),
                                    ('HB2', M.atom(H)),
                                    ('HB3', M.atom(H))),
                                   (('CB', 'HB1', "single"),
                                    ('CB', 'HB2', "single"),
                                    ('CB', 'HB3', "single"),))
        ala = M.fragment('alanine',
                         (('peptide', peptide_group),
                          ('sidechain', ala_sidechain)),
                         (),
                         (('peptide.CA', 'sidechain.CB', "single"),))
        ala_dipeptide = M.polymer('alanine_dipeptide',
                                  (('ALA1', ala),
                                   ('ALA2', ala)),
                                  (('ALA1.peptide.C', 'ALA2.peptide.N', "single"),),
                                  'polypeptide')
        self.universe = M.universe('cube', ((ala_dipeptide, 'di_ala', 2),),
                                   convention='my_own')
        self.assertTrue(is_valid(self.universe))

    def tearDown(self):
        TestHDF5Store.cleanup()


def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTest(loader.loadTestsFromTestCase(MMPeptideTest))
    s.addTest(loader.loadTestsFromTestCase(IMPeptideTest))
    return s

if __name__ == '__main__':
    unittest.main()
