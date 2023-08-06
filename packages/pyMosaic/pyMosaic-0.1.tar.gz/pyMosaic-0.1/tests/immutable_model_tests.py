# -*- coding: utf-8 -*-

# Tests for module mosaic.immutable_model
#
# Written by Konrad Hinsen
#

import unittest

import numpy as N
import immutable.np as IN

import mosaic.immutable_model as M
from mosaic.api import is_valid

def make_water_fragment(nsites=1):
    return M.fragment("water", (),
                      (("H1", M.atom(M.element("H"), nsites)),
                       ("H2", M.atom(M.element("H"), nsites)),
                       ("O",  M.atom(M.element("O"), nsites))),
                      (("H1", "O", "single"), ("H2", "O", "single")))


class AtomDescriptorTest(unittest.TestCase):

    def test_singleton(self):
        self.assertTrue(M.dummy() is M.dummy())
        self.assertTrue(M.dummy('a') is M.dummy('a'))
        self.assertTrue(M.dummy('a') is not M.dummy('b'))
        self.assertTrue(M.dummy('a') is not M.unknown('a'))
        self.assertTrue(M.dummy('C') is not M.element('C'))
        self.assertTrue(M.element('C') is M.element('C'))

    def test_name(self):
        for name in ['a', 'b', 'c']:
            self.assertEqual(M.unknown(name).name, name)

    def test_type(self):
        self.assertEqual(M.dummy().type, "dummy")
        self.assertEqual(M.unknown().type, "")
        self.assertEqual(M.element('O').type, "element")
        self.assertEqual(M.cgparticle('ala').type, "cgparticle")

class WaterTest(unittest.TestCase):

    def setUp(self):
        self.mol = make_water_fragment()

    def test_basics(self):
        self.assertEqual(self.mol.number_of_atoms, 3)
        self.assertEqual(self.mol.number_of_sites, 3)
        self.assertEqual(self.mol.number_of_bonds, 2)
        self.assertEqual(self.mol.species, "water")

    def test_equality(self):
        same_mol = make_water_fragment()
        changed_bond_order = M.fragment("water", (),
                                        (("H1", M.atom(M.element("H"))),
                                         ("H2", M.atom(M.element("H"))),
                                         ("O",  M.atom(M.element("O")))),
                                        (("O", "H2", "single"),
                                         ("O", "H1", "single")))
        changed_atom_order = M.fragment("water", (),
                                        (("O",  M.atom(M.element("O"))),
                                         ("H1", M.atom(M.element("H"))),
                                         ("H2", M.atom(M.element("H")))),
                                        (("O", "H1", "single"),
                                         ("O", "H2", "single")))
        self.assertEqual(self.mol, self.mol)
        self.assertEqual(self.mol, same_mol)
        self.assertEqual(self.mol, changed_bond_order)
        self.assertNotEqual(self.mol, changed_atom_order)
        
class PeptideTest(unittest.TestCase):

    def _make_molecule(self):
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
        return M.polymer('alanine_dipeptide',
                         (('ALA1', ala),
                          ('ALA2', ala)),
                         (('ALA1.peptide.C', 'ALA2.peptide.N', "single"),),
                         'polypeptide')

    def test_basic(self):
        mol = self._make_molecule()
        self.assertEqual(mol.number_of_atoms, 20)
        self.assertEqual(mol.number_of_sites, 20)
        self.assertEqual(mol.number_of_bonds, 19)
        self.assertEqual(mol.polymer_type, "polypeptide")

    def test_equality(self):
        self.assertEqual(self._make_molecule(),
                         self._make_molecule())

class ErrorCheckingTest(unittest.TestCase):

    def test_atom_descriptor(self):
        self.assertRaises(TypeError, lambda: M.dummy(42))
        self.assertRaises(ValueError, lambda: M.element(42))
        self.assertRaises(ValueError, lambda: M.element("X"))
        
    def test_atom(self):
        carbon = M.element("C")
        self.assertRaises(TypeError, lambda: M.atom('C', 1))
        self.assertRaises(ValueError, lambda: M.atom(carbon, 0))
        
    def test_fragment(self):
        carbon = M.atom(M.element("C"))
        # Illegal fragments
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', None, (("C", carbon),), ()))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', [1, 2], (("C", carbon),), ()))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (("C", carbon),), (), ()))
        # Illegal atoms
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), None, ()))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), [1, 2], ()))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), (carbon,), ()))
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (),
                                             (("C", carbon),
                                              ("C", carbon)),
                                             ()))
        # Illegal bond lists
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), (("C", carbon),), None))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), (("C", carbon),),
                                             [1, 2, 3]))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), (("C", carbon),),
                                             (('X', 'X'))))
        self.assertRaises(TypeError,
                          lambda: M.fragment('m', (), (("C", carbon),),
                                             (['X', 'X', 'single'])))
        
    def test_bonds(self):
        carbon = M.atom(M.element("C"))
        # Bond specified by only one atom
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (),
                                             (('C1', carbon), ('C2', carbon)),
                                             (('C1', ),)))
        # Bond specified by two atoms but no bond order
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (),
                                             (('C1', carbon), ('C2', carbon)),
                                             (('C1', 'C2'),)))
        # Bond specified by two identical atoms
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (),
                                             (('C1', carbon), ('C2', carbon)),
                                             (('C1', 'C1', ''),)))
        # Bond specified by an atom name that is undefined
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (),
                                             (('C1', carbon), ('C2', carbon)),
                                             (('C1', 'C3', ''),)))
        # Bond specified at the wrong fragment level
        f = M.fragment('x', (), (('C1', carbon), ('C2', carbon)), ())
        self.assertRaises(ValueError,
                          lambda: M.fragment('m', (('x', f),),
                                             (('C3', carbon),),
                                             (('x.C1', 'x.C2', ''),)))

    def test_universe(self):
        mol = M.fragment("water", (),
                         (("H1", M.atom(M.element("H"), 8)),
                          ("H2", M.atom(M.element("H"), 8)),
                          ("O",  M.atom(M.element("O"), 2))),
                         (("H1", "O", "single"), ("H2", "O", "single")))
        self.assertRaises(TypeError,
                          lambda: M.universe(0, [(mol, 'water', 10)]))
        self.assertRaises(ValueError,
                          lambda: M.universe('strange', [(mol, 'water', 10)]))
        self.assertRaises(ValueError,
                          lambda: M.universe('strange', [(mol, 10)]))
        self.assertRaises(TypeError,
                          lambda: M.universe('infinite', mol))
        self.assertRaises(ValueError,
                          lambda: M.universe('infinite', [("water", 10)]))
        self.assertRaises(TypeError,
                          lambda: M.universe('infinite', [mol]))
        self.assertRaises(ValueError,
                          lambda: M.universe('infinite', [(10, mol)]))

    def test_configuration(self):
        mol = make_water_fragment()
        universe = M.universe('cube', [(mol, 'water', 10)])
        # Missing data
        self.assertRaises(TypeError,
                          lambda: M.Configuration(universe))
        # Positions but no cell parameters
        self.assertRaises(TypeError,
                          lambda: M.Configuration(universe,
                                                  IN.zeros((30, 3), N.float32)))
        # Positions and cell parameters of different dtype
        self.assertRaises(ValueError,
                          lambda: M.Configuration(universe,
                                                  IN.zeros((30, 3), N.float32),
                                                  N.float64(10.)))
        # Positions not an array
        self.assertRaises(TypeError,
                          lambda: M.Configuration(universe,
                                                  list(IN.zeros((30, 3),
                                                               N.float32)),
                                                  N.float32(10.)))
        # Positions of wrong shape
        self.assertRaises(ValueError,
                          lambda: M.Configuration(universe,
                                                  IN.zeros((25, 3), N.float32),
                                                  N.float32(10.)))
        # Cell parameters of wrong shape
        self.assertRaises(ValueError,
                          lambda: M.Configuration(universe,
                                                  IN.zeros((30, 3), N.float32),
                                                  IN.zeros((3,), N.float32)))
        
class UniverseTest(unittest.TestCase):

    def setUp(self):
        mol = make_water_fragment(2)
        self.universe = M.universe('infinite', [(mol, 'water', 10)],
                                   convention='my_own')

    def test_basics(self):
        self.assertTrue(is_valid(self.universe))
        self.assertEqual(self.universe.number_of_molecules, 10)
        self.assertEqual(self.universe.number_of_atoms, 30)
        self.assertEqual(self.universe.number_of_sites, 60)
        self.assertEqual(self.universe.number_of_bonds, 20)
        self.assertEqual(self.universe.cell_shape, "infinite")
        self.assertEqual(self.universe.convention, "my_own")

    def test_properties(self):
        masses = M.TemplateAtomProperty(self.universe,
                                        "masses", "amu",
                                        IN.array([1., 1., 16.], N.float32))
        self.assertTrue(is_valid(masses))
        self.assertEqual(masses.type, 'template_atom')
        self.assertTrue(masses.universe == self.universe)
        self.assertEqual(masses.element_shape, ())
        self.assertEqual(masses.data.shape, (3,))
        bead_masses = M.TemplateSiteProperty(self.universe,
                                             "mass", "amu",
                                             IN.array([1., 1.,
                                                       1., 1.,
                                                       8., 8.], N.float32))
        self.assertTrue(is_valid(bead_masses))
        self.assertEqual(bead_masses.type, 'template_site')
        self.assertTrue(bead_masses.universe is self.universe)
        self.assertEqual(bead_masses.element_shape, ())
        self.assertEqual(bead_masses.data.shape, (6,))
        velocities = M.SiteProperty(self.universe,
                                    "velocity", "nm ps-1",
                                    IN.zeros((60, 3), dtype=N.float64))
        self.assertTrue(is_valid(velocities))
        self.assertEqual(velocities.type, 'site')
        self.assertTrue(velocities.universe is self.universe)
        self.assertEqual(velocities.data.shape, (60, 3))
        self.assertEqual(velocities.element_shape, (3,))
        foo = M.AtomProperty(self.universe,
                             "foo", "",
                             IN.zeros((30, 2, 2), dtype=N.int16))
        self.assertTrue(is_valid(foo))
        self.assertEqual(foo.type, 'atom')
        self.assertTrue(foo.universe is self.universe)
        self.assertEqual(foo.data.shape, (30, 2, 2))
        self.assertEqual(foo.element_shape, (2, 2))

    def test_labels(self):
        labels = tuple(a.name
                       for f, n in self.universe.molecules
                       for a in f.recursive_atom_iterator())
        el = M.TemplateAtomLabel(self.universe, "element", labels)
        self.assertTrue(is_valid(el))
        self.assertEqual(el.name, "element")
        self.assertTrue(el.universe == self.universe)
        self.assertTrue(len(el.strings)
                        == self.universe.number_of_template_atoms)
        for s1, s2 in zip(labels, el.strings):
            self.assertEqual(s1, s2)

        labels = tuple(a.name
                       for f, n in self.universe.molecules
                       for _ in range(n)
                       for a in f.recursive_atom_iterator())
        el = M.AtomLabel(self.universe, "element", labels)
        self.assertTrue(is_valid(el))
        self.assertEqual(el.name, "element")
        self.assertTrue(el.universe == self.universe)
        self.assertTrue(len(el.strings)
                        == self.universe.number_of_atoms)
        for s1, s2 in zip(labels, el.strings):
            self.assertEqual(s1, s2)

        labels = tuple(a.name
                       for f, n in self.universe.molecules
                       for a in f.recursive_atom_iterator()
                       for _ in range(a.number_of_sites))
        el = M.TemplateSiteLabel(self.universe, "element", labels)
        self.assertTrue(is_valid(el))
        self.assertEqual(el.name, "element")
        self.assertTrue(el.universe == self.universe)
        self.assertTrue(len(el.strings)
                        == self.universe.number_of_template_sites)
        for s1, s2 in zip(labels, el.strings):
            self.assertEqual(s1, s2)

        labels = tuple(a.name
                       for f, n in self.universe.molecules
                       for _ in range(n)
                       for a in f.recursive_atom_iterator()
                       for __ in range(a.number_of_sites))
        el = M.SiteLabel(self.universe, "element", labels)
        self.assertTrue(is_valid(el))
        self.assertEqual(el.name, "element")
        self.assertTrue(el.universe == self.universe)
        self.assertTrue(len(el.strings)
                        == self.universe.number_of_sites)
        for s1, s2 in zip(labels, el.strings):
            self.assertEqual(s1, s2)

class PBCTest(unittest.TestCase):

    def setUp(self):
        self.infinite = M.universe('infinite', ())
        self.cube = M.universe('cube', ())
        self.cuboid = M.universe('cuboid', ())
        self.parallelepiped = M.universe('parallelepiped', ())

    def test_lattice_vectors(self):
        conf = M.Configuration(self.infinite,
                               IN.zeros((0, 3), N.float32),
                               None)
        self.assertEqual(conf.lattice_vectors(), ())
        conf = M.Configuration(self.cube,
                               IN.zeros((0, 3), N.float32),
                               IN.array(1., N.float32))
        lv = conf.lattice_vectors()
        self.assertTrue((lv[0] == N.array([1., 0., 0.], N.float32)).all())
        self.assertTrue((lv[1] == N.array([0., 1., 0.], N.float32)).all())
        self.assertTrue((lv[2] == N.array([0., 0., 1.], N.float32)).all())
        conf = M.Configuration(self.cuboid,
                               IN.zeros((0, 3), N.float32),
                               IN.array([1., 2., 4.], N.float32))
        lv = conf.lattice_vectors()
        self.assertTrue((lv[0] == N.array([1., 0., 0.], N.float32)).all())
        self.assertTrue((lv[1] == N.array([0., 2., 0.], N.float32)).all())
        self.assertTrue((lv[2] == N.array([0., 0., 4.], N.float32)).all())
        conf = M.Configuration(self.parallelepiped,
                               IN.zeros((0, 3), N.float32),
                               IN.array([[1., 2., 4.],
                                         [8., 4., 2.],
                                         [16., 4., 8.]], N.float32))
        lv = conf.lattice_vectors()
        self.assertTrue((lv[0] == N.array([1., 2., 4.], N.float32)).all())
        self.assertTrue((lv[1] == N.array([8., 4., 2.], N.float32)).all())
        self.assertTrue((lv[2] == N.array([16., 4., 8.], N.float32)).all())


PBCTest('test_lattice_vectors').debug()

def suite():
    loader = unittest.TestLoader()
    s = unittest.TestSuite()
    s.addTest(loader.loadTestsFromTestCase(AtomDescriptorTest))
    s.addTest(loader.loadTestsFromTestCase(WaterTest))
    s.addTest(loader.loadTestsFromTestCase(PeptideTest))
    s.addTest(loader.loadTestsFromTestCase(ErrorCheckingTest))
    s.addTest(loader.loadTestsFromTestCase(UniverseTest))
    s.addTest(loader.loadTestsFromTestCase(PBCTest))
    return s

if __name__ == '__main__':
    unittest.main()
