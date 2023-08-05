"""
A SOAP implementation for wsme.
Parts of the code were taken from the tgwebservices soap implmentation.
"""

import pkg_resources
import datetime
import decimal
import base64
import logging

from simplegeneric import generic

try:
    from xml.etree import cElementTree as et
except ImportError:
    import cElementTree as et  # noqa

from genshi.builder import Element
from genshi.template import MarkupTemplate

from wsme.api import pexpose
from wsme.protocols import CallContext, Protocol

import wsme.types
from wsme import exc
from wsme.utils import parse_isodate, parse_isotime, parse_isodatetime

log = logging.getLogger(__name__)

xsi_ns = 'http://www.w3.org/2001/XMLSchema-instance'
type_qn = '{%s}type' % xsi_ns
nil_qn = '{%s}nil' % xsi_ns


type_registry = {
    wsme.types.bytes: 'xsd:string',
    wsme.types.text: 'xsd:string',
    int: 'xsd:int',
    long: "xsd:long",
    float: "xsd:float",
    bool: "xsd:boolean",
    #unsigned: "xsd:unsignedInt",
    datetime.datetime: "xsd:dateTime",
    datetime.date: "xsd:date",
    datetime.time: "xsd:time",
    decimal.Decimal: "xsd:decimal",
    wsme.types.binary: "xsd:base64Binary",
}

array_registry = {
    basestring: "String_Array",
    str: "String_Array",
    unicode: "String_Array",
    int: "Int_Array",
    long: "Long_Array",
    float: "Float_Array",
    bool: "Boolean_Array",
}


def soap_array(datatype):
    if datatype.item_type in array_registry:
        return array_registry[datatype.item_type]
    return soap_type(datatype.item_type, nons=True) + '_Array'


def soap_type(datatype, nons=False):
    ns = '' if nons else 'types:'
    if wsme.types.isarray(datatype):
        return ns + soap_array(datatype)
    if wsme.types.isdict(datatype):
        return None
    if datatype in type_registry:
        return type_registry[datatype]
    if wsme.types.iscomplex(datatype):
        return ns + datatype.__name__


def soap_fname(path, funcdef):
    return "".join([path[0]] + [i.capitalize() for i in path[1:]])


def make_soap_element(datatype, tag, value, xsitype=None):
    el = Element(tag)
    if value is None:
        el(**{'xsi:nil': 'true'})
    elif xsitype is not None:
        el(value, **{'xsi:type': xsitype})
    elif wsme.types.isusertype(datatype):
        return tosoap(
                datatype.basetype, tag,
                datatype.tobasetype(value))
    elif wsme.types.iscomplex(datatype):
        el(**{'xsi:type': datatype.__name__})
        for attrdef in wsme.types.list_attributes(datatype):
            attrvalue = getattr(value, attrdef.key)
            if attrvalue is not wsme.types.Unset:
                el.append(
                    tosoap(attrdef.datatype, attrdef.name, attrvalue)
                )
    else:
        el(value, **{'xsi:type': type_registry.get(datatype)})
    return el


@generic
def tosoap(datatype, tag, value):
    """Converts a value into xml Element objects for inclusion in the SOAP
    response output (after adding the type to the type_registry).

    If a non-complex user specific type is to be used in the api,
    a specific toxml should be added::

        from wsme.protocol.soap import tosoap, make_soap_element, type_registry

        class MySpecialType(object):
            pass

        type_registry[MySpecialType] = 'xsd:MySpecialType'

        @tosoap.when_object(MySpecialType)
        def myspecialtype_tosoap(datatype, tag, value):
            return make_soap_element(datatype, tag, str(value))
    """
    return make_soap_element(datatype, tag, value)


@tosoap.when_type(wsme.types.ArrayType)
def array_tosoap(datatype, tag, value):
    el = Element(tag)
    el(**{'xsi:type': soap_array(datatype)})
    if value is None:
        el(**{'xsi:nil': 'true'})
    elif len(value) == 0:
        el.append(Element('item'))
    else:
        for item in value:
            el.append(tosoap(datatype.item_type, 'item', item))
    return el


@tosoap.when_object(bool)
def bool_tosoap(datatype, tag, value):
    return make_soap_element(datatype, tag,
        value is True and 'true' or value is False and 'false' or None)


@tosoap.when_object(datetime.datetime)
def datetime_tosoap(datatype, tag, value):
    return make_soap_element(datatype, tag,
        value is not None and value.isoformat() or None)


@tosoap.when_object(wsme.types.binary)
def binary_tosoap(datatype, tag, value):
    return make_soap_element(datatype.basetype, tag,
        value is not None and base64.encodestring(value)
        or None,
        'xsd:base64Binary')


@tosoap.when_object(None)
def None_tosoap(datatype, tag, value):
    return make_soap_element(datatype, tag, None)


@generic
def fromsoap(datatype, el, ns):
    """
    A generic converter from soap elements to python datatype.

    If a non-complex user specific type is to be used in the api,
    a specific fromsoap should be added.
    """
    if el.get(nil_qn) == 'true':
        return None
    soaptype = soap_type(datatype, nons=True)
    if datatype in type_registry:
        if soaptype and soaptype != type_registry[datatype]:
            raise exc.InvalidInput(el.tag, et.tostring(el))
        value = datatype(el.text)
    elif wsme.types.isusertype(datatype):
        value = datatype.frombasetype(
            fromsoap(datatype.basetype, el, ns))
    else:
        if soaptype != datatype.__name__:
            raise exc.InvalidInput(el.tag, et.tostring(el))
        value = datatype()
        for attr in wsme.types.list_attributes(datatype):
            child = el.find('{%s}%s' % (ns['type'], attr.name))
            if child is not None:
                setattr(value, attr.key, fromsoap(attr.datatype, child, ns))
    return value


@fromsoap.when_type(wsme.types.ArrayType)
def array_fromsoap(datatype, el, ns):
    if len(el) == 1:
        if datatype.item_type \
                not in wsme.types.pod_types + wsme.types.dt_types \
                and len(el[0]) == 0:
            return []
    return [fromsoap(datatype.item_type, child, ns) for child in el]


@fromsoap.when_object(datetime.date)
def date_fromsoap(datatype, el, ns):
    if el.get(nil_qn) == 'true':
        return None
    if el.get(type_qn) != 'xsd:date':
        raise exc.InvalidInput(el.tag, et.tostring(el))
    return parse_isodate(el.text)


@fromsoap.when_object(datetime.time)
def time_fromsoap(datatype, el, ns):
    if el.get(nil_qn) == 'true':
        return None
    if el.get(type_qn) != 'xsd:time':
        raise exc.InvalidInput(el.tag, et.tostring(el))
    return parse_isotime(el.text)


@fromsoap.when_object(datetime.datetime)
def datetime_fromsoap(datatype, el, ns):
    if el.get(nil_qn) == 'true':
        return None
    if el.get(type_qn) != 'xsd:dateTime':
        raise exc.InvalidInput(el.tag, et.tostring(el))
    return parse_isodatetime(el.text)


@fromsoap.when_object(wsme.types.binary)
def binary_fromsoap(datatype, el, ns):
    if el.get(nil_qn) == 'true':
        return None
    if el.get(type_qn) != 'xsd:base64Binary':
        raise exc.InvalidInput(el.tag, et.tostring(el))
    return base64.decodestring(el.text)


class SoapProtocol(Protocol):
    """
    SOAP protocol.

    .. autoattribute:: name
    .. autoattribute:: content_types
    """
    name = 'soap'
    displayname = 'SOAP'
    content_types = ['application/soap+xml']

    ns = {
        "soap": "http://www.w3.org/2001/12/soap-envelope",
        "soapenv": "http://schemas.xmlsoap.org/soap/envelope/",
        "soapenc": "http://schemas.xmlsoap.org/soap/encoding/",
    }

    def __init__(self, tns=None,
            typenamespace=None,
            baseURL=None):
        self.tns = tns
        self.typenamespace = typenamespace
        self.servicename = 'MyApp'
        self.baseURL = baseURL
        self._name_mapping = {}

    def get_name_mapping(self, service=None):
        if service not in self._name_mapping:
            self._name_mapping[service] = dict(
                (soap_fname(path, f), path)
                for path, f in self.root.getapi()
                    if service is None or (path and path[0] == service))
        return self._name_mapping[service]

    def accept(self, req):
        if req.path.endswith('.wsdl'):
            return True
        for ct in self.content_types:
            if req.headers['Content-Type'].startswith(ct):
                return True
        if req.headers.get("Soapaction"):
            return True
        return False

    def iter_calls(self, request):
        yield CallContext(request)

    def extract_path(self, context):
        request = context.request
        if request.path.endswith('.wsdl'):
            return ['_protocol', self.name, 'api_wsdl']
        el = et.fromstring(request.body)
        body = el.find('{%(soapenv)s}Body' % self.ns)
        # Extract the service name from the tns
        message = list(body)[0]
        fname = message.tag
        if fname.startswith('{%s}' % self.typenamespace):
            fname = fname[len(self.typenamespace) + 2:]
            mapping = self.get_name_mapping()
            if fname not in mapping:
                raise exc.UnknownFunction(fname)
            path = mapping[fname]
            context.soap_message = message
            return path
        return None

    def read_arguments(self, context):
        kw = {}
        if not hasattr(context, 'soap_message'):
            return kw
        msg = context.soap_message
        for param in msg:
            name = param.tag[len(self.typenamespace) + 2:]
            arg = context.funcdef.get_arg(name)
            value = fromsoap(arg.datatype, param, {
                'type': self.typenamespace,
            })
            kw[name] = value

        return kw

    def soap_response(self, path, funcdef, result):
        r = Element(soap_fname(path, funcdef) + 'Response')
        r.append(tosoap(funcdef.return_type, 'result', result))
        return r

    def encode_result(self, context, result):
        envelope = self.render_template('soap',
                typenamespace=self.typenamespace,
                result=result,
                context=context,
                soap_response=self.soap_response)
        return envelope

    def get_template(self, name):
        return pkg_resources.resource_string(
            __name__, '%s.html' % name)

    def render_template(self, name, **kw):
        tmpl = MarkupTemplate(self.get_template(name))
        stream = tmpl.generate(**kw)
        return stream.render('xml')

    def encode_error(self, context, infos):
        return self.render_template('fault',
            typenamespace=self.typenamespace,
            **infos)

    @pexpose(contenttype="text/xml")
    def api_wsdl(self, service=None):
        if service is None:
            servicename = self.servicename
        else:
            servicename = self.servicename + service.capitalize()
        return self.render_template('wsdl',
            tns=self.tns,
            typenamespace=self.typenamespace,
            soapenc=self.ns['soapenc'],
            service_name=servicename,
            complex_types=(t() for t in self.root.__registry__.complex_types),
            funclist=self.root.getapi(),
            arrays=self.root.__registry__.array_types,
            list_attributes=wsme.types.list_attributes,
            baseURL=self.baseURL,
            soap_array=soap_array,
            soap_type=soap_type,
            soap_fname=soap_fname,
        )

    def encode_sample_value(self, datatype, value, format=False):
        r = make_soap_element(datatype, 'value', value)
        if format:
            xml_indent(r)
        return ('xml', unicode(r))


def xml_indent(elem, level=0):
    i = "\n" + level * "  "
    if elem.children:
        for e in elem.children:
            if isinstance(e, Element):
                xml_indent(e, level + 1)
        if isinstance(elem.children[0], Element):
            elem.children[:0] = i + '  '
        if isinstance(elem.children[-1], Element):
            elem(i)
    elif level:
        elem(i)
