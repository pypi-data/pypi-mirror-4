# -*- coding: utf-8 -*-
"""HDF5 I/O

Any model implementing the Mosaic API can be written to a HDF5 file,
but will be implicitly converted to an array_model representation.
Data items read from a HDF5 file are always represented by
an array_model.

The HDF5 storage layout is designed for clarity rather than
simplicity, the files should be as self-documenting as possible.

"""

import copy
import operator
import weakref

import h5py
import h5py.h5t
import h5py.h5d
import h5py.h5s
import h5py.version
import numpy as N

import mosaic.array_model
import mosaic.api as api
from mosaic.utility import MethodRegister
from mosaic.utility import ascii
from mosaic.utility import isstring
from mosaic.utility import py_str

import sys
del sys


if h5py.version.hdf5_version_tuple < (1, 8, 7):
    raise ValueError("HDF5 version >= 1.8.7 required")


def int_size_for_max_value(n):
    if n < 256:
        return N.uint8
    elif n < 65536:
        return N.uint16
    elif n < 4294967296:
        return N.uint32
    else:
        return N.uint64


def create_dataset(group, path, data):
    ds = group.require_dataset(path, shape=data.shape, dtype=data.dtype)
    if 0 not in data.shape:
        ds[...] = data
    return ds


class HDF5Store(object):

    def __init__(self, hdf5_group_or_filename, file_mode=None):
        if isstring(hdf5_group_or_filename):
            if file_mode is None:
                file_mode = 'r'
            self.root = h5py.File(hdf5_group_or_filename, file_mode)
            self._close = True
        else:
            api.validate_value(file_mode, [None], "file_mode")
            self.root = hdf5_group_or_filename
            self._close = False
        self._path_map = weakref.WeakKeyDictionary()
        self._data_map = weakref.WeakValueDictionary()
        self._factory = mosaic.array_model.Factory()

    def close(self):
        if self._close:
            self.root.file.close()
        self.root = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def flush(self):
        self.root.file.flush()

    storage_handler = MethodRegister()

    def store(self, path, data):
        api.validate_type(path, str, "path")
        if path[0] == "/":
            raise ValueError("absolute paths not allowed")
        api.validate_type(data, api.MosaicDataItem, "data")
        handler = self.storage_handler[type(data)]
        if handler is None:
            raise TypeError("Storage of %s not yet implemented"
                            % str(type(data)))
        handler(self, path, data)
        self._register_data_item(path, data)

    def retrieve(self, path_or_node):
        if isinstance(path_or_node, h5py.h5r.Reference):
            path_or_node = self.root[path_or_node]
        if isinstance(path_or_node, str):
            path = path_or_node
        else: # Group, Dataset, or classes with the same interface
            path = path_or_node.name
        if path[0] == '/':
            if path.startswith(self.root.name):
                path = path[len(self.root.name):]
                if path[0] == '/':
                    path = path[1:]
            else:
                raise ValueError("path name not inside root group")
        data = self._get_data(path)
        if data is not None:
            return data
        node = self.root[path]
        label = py_str(self._read_stamp(node))
        if label not in self._node_types:
            raise ValueError("Undefined node type %s" % label)
        handler = self.storage_handler[label]
        if handler is None:
            raise ValueError("Retrieval of node type %s not yet implemented"
                             % label)
        data = handler(self, node)
        self._register_data_item(path, data)
        return data

    _node_types = ['universe', 'configuration', 'property', 'label']

    def __iter__(self):
        # First pass: universes
        for name in self.root:
            node = self.root[name]
            if node.attrs['DATA_MODEL'] == ascii('MOSAIC') \
               and node.attrs['MOSAIC_DATA_TYPE'] == ascii('universe'):
                yield name, self.retrieve(node)
        # First pass: anything else
        for name in self.root:
            node = self.root[name]
            if node.attrs['DATA_MODEL'] == ascii('MOSAIC') \
               and node.attrs['MOSAIC_DATA_TYPE'] != ascii('universe'):
                yield name, self.retrieve(node)

    def _stamp(self, node, label):
        node.attrs['DATA_MODEL'] = ascii('MOSAIC')
        node.attrs['DATA_MODEL_MAJOR_VERSION'] = api.MOSAIC_VERSION[0]
        node.attrs['DATA_MODEL_MINOR_VERSION'] = api.MOSAIC_VERSION[1]
        node.attrs['MOSAIC_DATA_TYPE'] = ascii(label)

    def _read_stamp(self, node):
        if node.attrs['DATA_MODEL'] != ascii('MOSAIC'):
            raise ValueError("Node %s not an Mosaic data item" % str(node))
        version = (node.attrs['DATA_MODEL_MAJOR_VERSION'],
                   node.attrs['DATA_MODEL_MINOR_VERSION'])
        if version[0] > api.MOSAIC_VERSION[0] \
           or version[1] > api.MOSAIC_VERSION[1]:
            raise ValueError("HDF5 data is for version %d.%d, "
                             "software is version %d.%d"
                             % (version + api.MOSAIC_VERSION))
        return node.attrs['MOSAIC_DATA_TYPE']

    def _register_data_item(self, path, data_item):
        self._data_map[path] = data_item
        self._path_map[data_item] = path

    def _get_path(self, data_item):
        return self._path_map.get(data_item, None)

    def _get_data(self, path):
        return self._data_map.get(path, None)

    #
    # Store data in HDF5 file
    #
    @storage_handler(api.MosaicUniverse)
    def _store_universe(self, path, universe):
        group = self.root.require_group(path)
        try:
            # ActivePapers support
            group.mark_as_data_item()
        except AttributeError:
            pass
        self._stamp(group, 'universe')

        # Convert the universe to an array_model
        universe = self._factory(universe)

        # Create HDF5 datasets
        create_dataset(group, 'cell_shape',
                       data=N.array(universe.cell_shape, 'S'))
        create_dataset(group, 'symmetry_transformations',
                       data=N.array(universe._symmetry_transformations))
        create_dataset(group, 'convention',
                       data=N.array(universe.convention, 'S'))
        create_dataset(group, 'fragments', data=universe._fragment_array)
        create_dataset(group, 'atoms', data=universe._atom_array)
        create_dataset(group, 'bonds', data=universe._bond_array)
        create_dataset(group, 'molecules', data=universe._molecule_array)
        if len(universe._polymer_array) > 0:
            create_dataset(group, 'polymers', data=universe._polymer_array)
        symbols = universe._symbols
        symbol_table = group.require_dataset('symbols',
                                shape=(len(symbols),),
                                dtype=h5py.special_dtype(vlen=bytes))
        for i, s in enumerate(symbols):
            symbol_table[i] = ascii(s)

    @storage_handler(api.MosaicConfiguration)
    def _store_configuration(self, path, configuration):
        universe = configuration.universe
        universe_path = self._get_path(universe)
        if universe_path is None:
            raise IOError("universe must be stored first")
        group = self.root.require_group(path)
        try:
            # ActivePapers support
            group.mark_as_data_item()
        except AttributeError:
            pass
        self._stamp(group, 'configuration')
        group.attrs['universe'] = self.root[universe_path].ref
        ncellparams = N.multiply.reduce(universe.cell_parameter_array_shape)
        if ncellparams > 0:
            create_dataset(group, 'cell_parameters',
                           data=configuration.cell_parameters)
        arr = N.ascontiguousarray(configuration.positions)
        positions = group.require_dataset('positions',
                                          shape=(len(arr),),
                                          dtype='(3,)f%d' % arr.dtype.itemsize)
        # There doesn't seem to be any way to write this array
        # using high-level operations, so we use the low-level access.
        mtype = h5py.h5t.py_create(positions.id.dtype)
        mspace = h5py.h5s.create_simple(positions.shape)
        fspace = positions.id.get_space()
        positions.id.write(mspace, fspace, arr, mtype)

    @storage_handler(api.MosaicProperty)
    def _store_property(self, path, property):
        universe = property.universe
        universe_path = self._get_path(universe)
        if universe_path is None:
            raise IOError("universe must be stored first")
        element_shape = property.data.shape[1:]
        if element_shape:
            dtype = N.dtype((property.data.dtype, element_shape))
        else:
            dtype = property.data.dtype
        arr = N.ascontiguousarray(property.data)
        ds = self.root.require_dataset(path,
                                       shape=(len(arr),),
                                       dtype=dtype)
        self._stamp(ds, 'property')
        ds.attrs['universe'] = self.root[universe_path].ref
        ds.attrs['name'] = ascii(property.name)
        ds.attrs['units'] = ascii(property.units)
        ds.attrs['property_type'] = ascii(property.type)
        # There doesn't seem to be any way to write this array
        # using high-level operations, so we use the low-level access.
        mtype = h5py.h5t.py_create(ds.id.dtype)
        mspace = h5py.h5s.create_simple(ds.shape)
        fspace = ds.id.get_space()
        ds.id.write(mspace, fspace, arr, mtype)

    @storage_handler(api.MosaicLabel)
    def _store_label(self, path, label):
        universe = label.universe
        label = self._factory(label)
        universe_path = self._get_path(universe)
        if universe_path is None:
            raise IOError("universe must be stored first")
        ds = create_dataset(self.root, path, data=label._string_array)
        self._stamp(ds, 'label')
        ds.attrs['universe'] = self.root[universe_path].ref
        ds.attrs['name'] = ascii(label.name)
        ds.attrs['label_type'] = ascii(label.type)

    #
    # Retrieve data from HDF5 file
    #
    @storage_handler('universe')
    def _retrieve_universe(self, node):
        # Work around a restriction/bug in h5py that prevents reading
        # arrays of length zero.
        if node['symmetry_transformations'].shape[0] == 0:
            st = N.zeros((0,), dtype=node['symmetry_transformations'].dtype)
        else:
            st = node['symmetry_transformations'][...]
        return mosaic.array_model.Universe.from_arrays(
                        node['atoms'][...],
                        node['bonds'][...],
                        node['fragments'][...],
                        node['polymers'][...]
                            if 'polymers' in node else None,
                        node['molecules'][...],
                        tuple(py_str(s) for s in node['symbols'][...]),
                        st,
                        py_str(node['cell_shape'][...]),
                        py_str(node['convention'][...]))

    @storage_handler('configuration')
    def _retrieve_configuration(self, node):
        universe = self.retrieve(node.attrs['universe'])
        if 'cell_parameters' in node:
            ds = node['cell_parameters']
            cell_parameters = N.empty(ds.shape, ds.dtype)
            cell_parameters[...] = ds[...]
        else:
            cell_parameters = None
        positions = node['positions'][...]
        return mosaic.array_model.Configuration(universe, positions,
                                                cell_parameters)

    @storage_handler('property')
    def _retrieve_property(self, node):
        universe = self.retrieve(node.attrs['universe'])
        data = node[...]
        name = py_str(node.attrs['name'])
        units = py_str(node.attrs['units'])
        property_type = py_str(node.attrs['property_type'])
        return mosaic.array_model.Property(universe, name, units,
                                           data, property_type)

    @storage_handler('label')
    def _retrieve_label(self, node):
        universe = self.retrieve(node.attrs['universe'])
        data = node[...]
        name = py_str(node.attrs['name'])
        label_type = py_str(node.attrs['label_type'])
        return mosaic.array_model.Label.from_arrays(universe, name,
                                                    data, label_type)
