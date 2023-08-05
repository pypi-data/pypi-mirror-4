import numpy


class Dimension(object):
    def __init__(self, length):
        self.length = length


class Variable(object):
    def __init__(self, data, dimensions=None, record=False, **kwargs):
        # replace masked data --if any-- with missing_value.
        missing_value = (
                kwargs.get('missing_value') or
                kwargs.get('_FillValue') or 
                getattr(data, 'fill_value', None))
        if missing_value is not None:
            kwargs.setdefault('missing_value', missing_value)
            kwargs.setdefault('_FillValue', missing_value)
            self.data = numpy.ma.asarray(data).filled(missing_value)
        else:
            self.data = numpy.asarray(data)

        self.dimensions = dimensions
        self.record = record
        self.attributes = kwargs


class Group(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class NetCDF(object):
    @classmethod
    def save(klass, filename, **kwargs):
        # find netcdf loader
        if hasattr(klass, 'loader') and callable(getattr(klass, 'loader')):
            loader = getattr(klass, 'loader')
        else:
            from pupynere import netcdf_file as loader
        out = loader(filename, 'w', **kwargs)
        process(klass, out)
        out.close()


def process(obj, target):
    # add attributes
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, basestring) and not name.startswith('_'):
            setattr(target, name, attr)

    # set variable names from the class
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, (Variable, Dimension)):
            attr.name = name

    # add explicitly defined dimensions
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Dimension):
            target.createDimension(name, attr.length)

    # add groups
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Group):
            group = target.createGroup(name)
            process(attr, group)

    # add variables, and add their dimensions if necessary
    for name in dir(obj):
        attr = getattr(obj, name)
        if isinstance(attr, Variable):
            # add dimension?
            if attr.dimensions is None:
                attr.dimensions = [ attr ]
            for dim in attr.dimensions:
                if dim.name not in target.dimensions:
                    if dim.record:
                        target.createDimension(dim.name, None)
                    else:
                        target.createDimension(dim.name, len(dim.data))

            # create var
            if attr.data.dtype == numpy.int64:
                attr.data = attr.data.astype(numpy.int32)
            var = target.createVariable(
                    attr.name, 
                    attr.data.dtype, 
                    tuple(dim.name for dim in attr.dimensions))
            var[:] = attr.data[:]
            for k, v in attr.attributes.items():
                setattr(var, k, v)
