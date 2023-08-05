#!/usr/bin/python
# -*- coding: utf-8 -*-
#This file is part of pydsl.
#
#pydsl is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#pydsl is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with pydsl.  If not, see <http://www.gnu.org/licenses/>.

"""Python Transformers"""

__author__ = "Nestor Arocha"
__copyright__ = "Copyright 2008-2013, Nestor Arocha"
__email__ = "nesaro@gmail.com"

from .Channel import HostChannel
from pydsl.Exceptions import ProcessingError
import logging
LOG = logging.getLogger("PythonTransformer")


class PythonTransformer(HostChannel):
    """ Python function based transformer """
    def __init__(self, inputdic, outputdic, function):
        HostChannel.__init__(self, inputdic, outputdic)
        self._function = function

    def __call__(self, *args, **kwargs):
        if kwargs:
            for inputkey in self.inputchanneldic.keys():
                if inputkey not in kwargs:
                    raise KeyError("Key %s not found in inputdic" % inputkey)
            ibdic = kwargs
        elif len(args) == 1 and isinstance(args[0], dict):
            ibdic = args[0]
        elif len(args) == 1:
            ibdic = {list(self.inputchanneldic.keys())[0]:args[0]}
        else:
            raise ValueError
        for dickey in ibdic.keys():
            if not self.inputchanneldic[dickey].check(ibdic[dickey]):
                raise ValueError("Invalid value %s for input %s (%s)" % (ibdic[dickey], dickey, self))
        result = self._functionwrapper(ibdic)
        return result

    def _functionwrapper(self, wdict):
        """Wraps function call, to add parammeters if required"""
        LOG.debug("PythonTransformer._functionwrapper: begin")
        if hasattr(self, "_hostT"):
            result = self._function(wdict, self._hostT, self.inputchanneldic, self.outputchanneldic)
        else:
            result = self._function(wdict, self.inputchanneldic, self.outputchanneldic)
        if not result:
            raise ProcessingError("Transformer", self)
        for outputgrammarname in self.outputchanneldic.keys():
            LOG.debug("Verifying Grammar name: " + outputgrammarname)
            if not outputgrammarname in result:
                LOG.error("Error while verifying Grammar name:" + outputgrammarname)
                raise ProcessingError("Transformer")
        return result

    def __str__(self):
        return "<PythonTransformer: %s, %s" % (self.inputdefinition, self.outputdefinition)

    @property
    def summary(self):
        from pydsl.Abstract import InmutableDict
        inputdic = tuple(self.inputdefinition.values())
        outputdic = tuple(self.outputdefinition.values())
        result = {"iclass": "PythonTransformer", "input": inputdic, "output": outputdic}
        return InmutableDict(result)


class HostPythonTransformer(PythonTransformer):
    """Python Function Transformer which can call to other functions"""
    def __init__(self, inputdic, outputdic, auxdic, function):
        PythonTransformer.__init__(self, inputdic, outputdic, function)
        self._hostT = {}
        self._initHostT(auxdic)

    def _initHostT(self, namedic):
        """Inits auxiliary transformers """
        from pydsl.Memory.Loader import load
        for title, gttype in namedic.items():
            self._hostT[title] = load(gttype)
            LOG.debug("loaded " + str(title) + "auxT")
