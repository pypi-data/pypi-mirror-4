"""
Here are the validators
"""


from lxml import etree
from datetime import datetime

from eeml.unit import Unit
from eeml.util import _assertPosInt

class Version051(object):

#    VERSION = "0.5.1"
#    NAMESPACE = 'http://www.eeml.org/xsd/{}'.format(VERSION)
#    NSMAP = {None: NAMESPACE,
#         'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

#    def __init__(self):
        # self.VERSION = "0.5.1"
        # self.NAMESPACE = 'http://www.eeml.org/xsd/{}'.format(self.VERSION)

    def environment(self, env):
        status = env._status
        id_ = env._id
        private = env._private
        
        if status is not None and status not in ['frozen', 'live']:
            raise ValueError("status must be either 'frozen' or 'live', "
                             "got {}".format(status))
        _assertPosInt(id_, 'id', False)
        if private is not None and not isinstance(private, bool):
            raise ValueError("private is expected to be bool, got {}"
                             .format(type(private)))

    def location(self, loc):
        exposure = loc._exposure
        domain = loc._domain
        disposition = loc._disposition
        # TODO validate lat and lon

        if exposure is not None and exposure not in ['indoor', 'outdoor']:
            raise ValueError("exposure must be 'indoor' or 'outdoor', got '{}'"
                             .format(exposure))

        if domain not in ['physical', 'virtual']:
            raise ValueError("domain is required, must be 'physical' or "
                             "'virtual', got '{}'".format(domain))

        if disposition is not None and disposition not in ['fixed', 'mobile']:
            raise ValueError("disposition must be 'fixed' or 'mobile', got '{}'"
                             .format(disposition))

    def data(self, data):
        unit = data._unit
        at = data._at
        id_ = data._id

        _assertPosInt(id_, 'id', True)
        if unit is not None and not isinstance(unit, Unit):
            raise ValueError("unit must be an instance of Unit, got {}"
                             .format(type(unit)))
        if at is not None and not isinstance(at, datetime):
            raise ValueError("at must be an instance of datetime.datetime, "
                             "got {}".format(type(at)))


    def element(self, name):
        """
        Create an element in the EEML namespace
        """
        # return etree.Element("{{{}}}{}".format(self.NAMESPACE, name), nsmap=self.NSMAP)
        return etree.Element("{{{}}}{}".format('', name), nsmap={})

    def datapoints(self, datapoints):
        id_ = datapoints._id

        _assertPosInt(id_, 'id', True)


    def attribute(self, elem, value, name, call=lambda x: x):
        if value is not None:
            elem.attrib[name] = call(value)

    def child(self, elem, name, value, call=lambda x: x):
        if value is not None:
            tmp = self.element(name)
            tmp.text = call(value)
            elem.append(tmp)

class Invalidator(object):

    def __init__(self):
        self.VERSION = None

    def environment(self, env):
        pass

    def location(self, loc):
        pass

    def data(self, data):
        pass

    def datapoints(self, datapoints):
        pass


DEFAULTVALIDATOR = Version051
