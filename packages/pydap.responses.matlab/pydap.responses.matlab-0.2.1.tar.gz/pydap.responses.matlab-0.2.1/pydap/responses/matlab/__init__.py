from StringIO import StringIO

import numpy
from scipy.io import savemat

from pydap.model import *
from pydap.lib import walk
from pydap.responses.lib import BaseResponse


class MatlabResponse(BaseResponse):

    __description__ = "Matlab v5 file"

    def __init__(self, dataset):
        BaseResponse.__init__(self, dataset)
        self.headers.extend([
                ('Content-description', 'dods_matlab'),
                ('Content-type', 'application/x-matlab'),
                ])

    @staticmethod
    def serialize(dataset):
        buf = StringIO()
        mdict = { dataset.name: {} }
        target = mdict[dataset.name]

        # Global attributes. We need to skip empty dictionaries since savemat
        # doesn't work with them.
        if dataset.attributes:
            target['attributes'] =  dataset.attributes.copy()
        
        # Gridded data.
        for grid in walk(dataset, GridType):
            target = mdict[dataset.name][grid.name] = {}
            # Add dimensions.
            for map_ in grid.maps.values():
                target[map_.name] = { 
                    'data': numpy.asarray(map_, dtype='f'),
                }
                if map_.attributes:
                    target[map_.name]['attributes'] = map_.attributes.copy()
            # Add the var.
            target[grid.array.name] = {
                'data': numpy.asarray(grid.array, dtype='f'),
            }
            if grid.array.attributes:
                target[grid.array.name]['attributes'] = grid.array.attributes.copy()

        # Sequences.
        for seq in walk(dataset, SequenceType):
            target = mdict[dataset.name][seq.name] = {}
            # Add vars.
            for child in seq.walk():
                target[child.name] = {
                    'data': numpy.fromiter(child.data, child.type.typecode),
                }
                if child.attributes:
                    target[child.name]['attributes'] = child.attributes.copy()

        savemat(buf, mdict)
        return [ buf.getvalue() ]
                    

def save(dataset, filename):
    f = open(filename, 'w')
    f.write(MatlabResponse(dataset).serialize(dataset)[0])
    f.close()


if __name__ == '__main__':
    import numpy

    dataset = DatasetType(name='foo', attributes={'history': 'Test file created by Matlab response', 'version': 1.0})
    
    dataset['grid'] = GridType(name='grid')
    data = numpy.arange(6)
    data.shape = (2,3)
    dataset['grid']['array'] = BaseType(data=data, name='array', shape=data.shape, type=data.dtype.char)
    x, y = numpy.arange(2), numpy.arange(3) * 10
    dataset['grid']['x'] = BaseType(name='x', data=x, shape=x.shape, type=x.dtype.char, attributes={'units': 'm/s'})
    dataset['grid']['y'] = BaseType(name='y', data=y, shape=y.shape, type=y.dtype.char, attributes={'units': 'degC'})

    seq = dataset['seq'] = SequenceType(name='seq')
    seq['xval'] = BaseType(name='xval', type=Int16)
    seq['xval'].attributes['units'] = 'meters per second'
    seq['yval'] = BaseType(name='yval', type=Int16)
    seq['yval'].attributes['units'] = 'kilograms per minute'
    seq['zval'] = BaseType(name='zval', type=Int16)
    seq['zval'].attributes['units'] = 'tons per hour'
    seq.data = [(1, 2, 1), (2, 4, 4), (3, 6, 9), (4, 8, 16)]

    dataset._set_id()

    save(dataset, 'test.mat')
