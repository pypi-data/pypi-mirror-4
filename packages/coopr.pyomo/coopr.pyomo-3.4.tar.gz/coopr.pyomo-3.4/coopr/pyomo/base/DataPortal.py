#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['DataPortal']

import logging
from coopr.pyomo.base.plugin import *

logger = logging.getLogger('coopr.pyomo')

class DataPortal(object):
    """
    An object that manages data imports and exports from
    external data sources.

    This object contains the interface routines for importing and
    exporting data from external data sources.
    """

    def __init__(self, **kwds):
        """
        Constructor
        """
        # Initialize this object with no data manager
        self.data_manager = None

        # maps initialization data as follows: _data[namespace][symbol] -> data
        self._data={}

        # This is the data that is imported from various sources
        self._default={}

        # the model for which this data is associated. used for error
        # checking, e.g., object names must exist in the model, set 
        # dimensions must match, etc.
        self._model = kwds.pop('model', None)

        if 'filename' in kwds:
            filename = kwds.pop('filename')
            self.connect(filename=filename, **kwds)
            self.load()
            self.disconnect()
        elif 'data_dict' in kwds:
            data = kwds.pop('data_dict')
            if not data is None:
                self._data = data
        elif len(kwds) > 0:
            raise ValueError("Unknown options: %s" % str(kwds.keys()))

    #
    # intent of this method is to add, on a component-by-component 
    # basis, initialization data to a ModelData instance. not the
    # "usual" form of data initialization.
    #
    def Xinitialize(self, component, data, namespace=None):
        if namespace not in self._data.keys():
            self._data[namespace]={}
        self._data[namespace][component] = data

    def connect(self, **kwds):
        """
        Construct a data source objects that is associated with the input source.
        This data manager is used to process future data imports and exports.
        """
        if not self.data_manager is None:
            self.data_manager.close()
        data = kwds.get('filename',None)
        if data is None:
            data = kwds.get('server',None)
        tmp = data.split(".")[-1]
        self.data_manager = DataManagerFactory(tmp) 
        if self.data_manager is None:
            raise IOError("Unknown file format '%s'" % tmp)
        self.data_manager.initialize(**kwds)
        self.data_manager.open()

    def disconnect(self):
        """
        Close the Construct a data source objects that is associated with the input source.
        This data manager is used to process future data imports and exports.
        """
        self.data_manager.close()
        self.data_manager = None
        
    def load(self, **kwds):
        """
        Import data from an external data source.
        """
        _model = kwds.pop('model', None)
        if not _model is None:
            self._model=_model
        if __debug__:
            logger.debug("Loading data...")
        _disconnect=False
        if self.data_manager is None:
            self.connect(**kwds)
            _disconnect=True
        elif len(kwds) > 0:
            self.data_manager.add_options(**kwds)
        self._preprocess()
        if not self.data_manager.read():
            print("Warning: error occured while processing %s" % str(self.data_manager))
        if __debug__:
            logger.debug("Processing data ...")
        status = self.data_manager.process(self._model, self._data, self._default)
        self.data_manager.clear()
        if _disconnect:
            self.disconnect()
        if __debug__:
            logger.debug("Done.")

    def store(self, **kwds):
        """
        Export data from to an external data source.
        """
        if __debug__:
            logger.debug("Storing data...")
        _disconnect=False
        if self.data_manager is None:
            self.connect(**kwds)
            _disconnect=True
        elif len(kwds) > 0:
            self.data_manager.add_options(**kwds)
        self._preprocess()
        self.load_data()
        if not self.data_manager.write(self._data):
            print("Warning: error occured while processing %s" % str(self.data_manager))
        if _disconnect:
            self.disconnect()
        if __debug__:
            logger.debug("Done.")

    def data(self, name, namespace=None):
        if not namespace in self._data:
            raise IOError("Unknown namespace '%s'" % str(namespace))
        ans = self._data[namespace][name]
        if None in ans:
            return ans[None]
        return ans

    def _preprocess(self):
        options = self.data_manager.options
        #
        if options.data is None and (not options.set is None or not options.param is None or not options.index is None):
            options.data = []
            if not options.set is None:
                if type(options.set) in (list,tuple):
                    for item in options.set:
                        options.data.append(item)
                else:
                    options.data.append(options.set)
            if not options.index is None:
                options.data.append(options.index)
            if not options.param is None:
                if type(options.param) in (list,tuple):
                    for item in options.param:
                        options.data.append(item)
                else:
                    options.data.append(options.param)
        #
        if not options.data is None:
            if type(options.data) in (list, tuple):
                ans = []
                for item in options.data:
                    try:
                        ans.append(item.name)
                        self._model = item.model()
                    except:
                        ans.append(item)
                options.data = ans
            else:
                try:
                    self._model = options.data.model()
                    options.data = self.data_manager.options.data.name
                except:
                    pass


    def load_data(self):
        if not self.data_manager.options.data is None:
            if not self._model is None:
                if type(self.data_manager.options.data) is list:
                    for name in self.data_manager.options.data:
                        c = getattr(self._model, name)
                        try:
                            self._data[name] = c.data()
                        except:
                            self._data[name] = c.extract_values()
                else:
                    name = self.data_manager.options.data
                    c = getattr(self._model, name)
                    try:
                        self._data[name] = c.data()
                    except:
                        self._data[name] = c.extract_values()
 
