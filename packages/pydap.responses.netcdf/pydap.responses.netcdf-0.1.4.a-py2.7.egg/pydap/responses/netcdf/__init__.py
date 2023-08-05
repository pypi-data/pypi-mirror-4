from StringIO import StringIO
import itertools

import numpy

from pupynere import netcdf_file

from pydap.model import *
from pydap.lib import walk
from pydap.responses.lib import BaseResponse


class NetCDFResponse(BaseResponse):

    __description__ = "NetCDF file"

    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
                ('Content-description', 'dods_netcdf'),
                ('Content-type', 'application/x-netcdf'),
                ])

    @staticmethod
    def serialize(dataset):
        buf = StringIO()
        f = netcdf_file(buf, 'w')

        # Global attributes.
        nc_global = dataset.attributes.pop('NC_GLOBAL', {})
        for k, v in nc_global.items():
            if not isinstance(v, dict):
                setattr(f, k, v)
        for k, v in dataset.attributes.items():
            if not isinstance(v, dict):
                setattr(f, k, v)
        
        # Gridded data.
        for grid in walk(dataset, GridType):
            # Add dimensions.
            for dim, map_ in grid.maps.items():
                if dim not in f.dimensions:
                    # check if this is a record dimension
                    if ('DODS_EXTRA' in dataset.attributes and 
                            dataset.attributes['DODS_EXTRA']['Unlimited_Dimension'] == dim):
                        length = None
                    else:
                        length = map_.shape[0]
                    f.createDimension(dim, length)
                    var = f.createVariable(dim, map_.type.typecode, (dim,))
                    var[:] = numpy.asarray(map_)
                    for k, v in map_.attributes.items():
                        if not isinstance(v, dict):
                            setattr(var, k, v)
            # Add the var.
            var = f.createVariable(grid.name, grid.type.typecode, grid.dimensions)
            var[:] = numpy.asarray(grid.array)
            for k, v in grid.attributes.items():
                if not isinstance(v, dict):
                    setattr(var, k, v)

        # Sequences.
        for seq in walk(dataset, SequenceType):
            n = len(seq.data)
            dim, i = 'axis_0', 0
            while dim in f.dimensions:
                i += 1
                dim = 'axis_%d' % i
            f.createDimension(dim, None)
            var = f.createVariable(dim, 'i', (dim,))
            var[:] = numpy.arange(n)
            var.indexOf = seq.name

            # Add vars.
            for child in seq.walk():
                if child.type.typecode == 'S':
                    data = map(str, child.data)
                    n = max(map(len, data))
                    dim2, i = 'string_0', 0
                    while dim2 in f.dimensions:
                        i += 1
                        dim2 = 'string_%d' % i
                    f.createDimension(dim2, n)
                    data = numpy.array(map(list, data))
                    var = f.createVariable(child.name, child.type.typecode, (dim, dim2))
                    var[:] = numpy.array(data, child.type.typecode)
                else:
                    var = f.createVariable(child.name, child.type.typecode, (dim,))
                    var[:] = numpy.fromiter(child.data, child.type.typecode)
                for k, v in child.attributes.items():
                    if not isinstance(v, dict):
                        setattr(var, k, v)

        f.flush()
        return [ buf.getvalue() ]
                    

def save(dataset, filename):
    f = open(filename, 'w')
    f.write(NetCDFResponse(dataset).serialize(dataset)[0])
    f.close()


if __name__ == '__main__':
    import numpy

    dataset = DatasetType(name='foo')
    dataset['grid'] = GridType(name='grid')
    data = numpy.arange(6)
    data.shape = (2,3)
    dataset['grid']['array'] = BaseType(data=data, name='array', shape=data.shape, type=data.dtype.char)
    x, y = numpy.arange(2), numpy.arange(3) * 10
    dataset['grid']['x'] = BaseType(name='x', data=x, shape=x.shape, type=x.dtype.char)
    dataset['grid']['y'] = BaseType(name='y', data=y, shape=y.shape, type=y.dtype.char)
    dataset._set_id()

    save(dataset, 'test.nc')
