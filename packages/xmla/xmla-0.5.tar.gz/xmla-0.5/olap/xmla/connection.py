'''
Created on 18.04.2012

@author: norman
'''
from olap.xmla.interfaces import XMLAException
from suds.client import Client
from suds import WebFault
import http
import types
from formatreader import TupleFormatReader
from utils import *

from suds.plugin import MessagePlugin

# the following along with changes to the wsdl (elementFormDefault="unqualified") is needed
# to make it fly with icCube, which expects elements w/o namespace prefix
class UseDefaultNamespace(MessagePlugin):
    def marshalled(self, context):
        for d in context.envelope.getChild('Body').children:
            d.prefix = None
            d.set("xmlns", "urn:schemas-microsoft-com:xml-analysis")

#import logging
#logging.basicConfig(level=logging.INFO)
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)

# map of rowset: 
#   key   : XMLA rowset name
#   value : if empty, a query result for such a resultset will be returned as a list
#           the result will be returned as a dictionary keyed on a property 
#           of the resulting row which name this value represents
xmla1_1_rowsets = {"DISCOVER_DATASOURCES":"",
                   "DISCOVER_PROPERTIES":"PropertyName", 
                   "DISCOVER_SCHEMA_ROWSETS":"SchemaName",
                   "DISCOVER_ENUMERATORS":"",
                   "DISCOVER_LITERALS":"",
                   "DISCOVER_KEYWORDS":"",
                   "DBSCHEMA_CATALOGS":"CATALOG_NAME",
                   "DBSCHEMA_COLUMNS":"",
                   "DBSCHEMA_TABLES":"",
                   "DBSCHEMA_TABLES_INFO":"",
                   "DBSCHEMA_PROVIDER_TYPES":"TYPE_NAME",
                   "MDSCHEMA_ACTIONS":"",
                   "MDSCHEMA_CUBES":"",
                   "MDSCHEMA_DIMENSIONS":"",
                   "MDSCHEMA_FUNCTIONS":"",
                   "MDSCHEMA_HIERARCHIES":"",
                   "MDSCHEMA_MEASURES":"",
                   "MDSCHEMA_MEMBERS":"",
                   "MDSCHEMA_PROPERTIES":"",
                   "MDSCHEMA_SETS":""
                   }

class XMLAConnection(object):
    
    @classmethod
    def addMethod(cls, funcname, func):
        return setattr(cls, funcname, types.MethodType(func, None, cls))

        
    @classmethod
    def setupMembers(cls):
        def getFunc(schemaName, keyname):
            return lambda this, *args, **kw: cls.Discover(this, 
                                                          schemaName, 
                                                          keyname, 
                                                          *args, **kw)
        
        for schemaName, keyname in xmla1_1_rowsets.items():
            mname = schemaNameToMethodName(schemaName)
            cls.addMethod( mname, getFunc(schemaName, keyname) )

    def __init__(self, url, location, username, password, spn, sslverify):

        if password is None:
            transport = http.HttpKerberosAuthenticated(as_user=username, 
                                                       spn=spn, 
                                                       sslverify=sslverify)
        else:
            transport = http.HttpAuthenticated(username=username, 
                                               password=password, 
                                               sslverify=sslverify)
        self.client = Client(url, 
                             location=location, 
                             transport=transport, 
                             cache=None, 
                             plugins=[UseDefaultNamespace()])
        
        # optional, call might fail
        self.getMDSchemaLevels = lambda *args, **kw: self.Discover("MDSCHEMA_LEVELS", 
                                                                   None, *args, **kw)
        self.sessionid = None
             
        
    def Discover(self, what, keyname=None, restrictions=None, properties=None):
        rl = None
        pl = None
        if restrictions:
            rl = {"RestrictionList":restrictions}
        if properties:
            pl = {"PropertyList":properties}
            
        try:
            res = getattr(self.client.service.Discover(what, rl, pl).\
                              DiscoverResponse["return"].root, "row", [])
            if res:
                if keyname:
                    res = mapify(res, keyname)
                else:
                    res = listify(res)
        except WebFault, fault:
            raise XMLAException(fault.message, listify(fault.fault))
        return res


    def Execute(self, command, dimformat="Multidimensional", 
                axisFormat="TupleFormat", **kwargs):
        if isinstance(command, types.StringTypes):
            command = {"Statement":command}
        props = {"Format":dimformat, "AxisFormat":axisFormat}
        props.update(kwargs)
        pl = {"PropertyList":props}
        try:
            root = self.client.service.Execute(command, pl).ExecuteResponse["return"].root
            return TupleFormatReader(root)
        except WebFault, fault:
            raise XMLAException(fault.message, listify(fault.fault))
        
        
    def BeginSession(self):
        bs= self.client.factory.create("BeginSession")
        bs._mustUnderstand = 1
        sess= self.client.factory.create("Session")
        sess._mustUnderstand = 1
        self.client.set_options(soapheaders={"BeginSession":bs})
        self.client.service.Execute({"Statement":None})
        sess._SessionId=self.client.last_received().\
            childAtPath("/Envelope/Header/Session").getAttribute("SessionId").getValue()
        self.sessionid = sess._SessionId
        self.client.set_options(soapheaders=sess)
        
    def EndSession(self):
        if self.sessionid is not None:
            es= self.client.factory.create("EndSession")
            es._mustUnderstand = 1
            es._SessionId = self.sessionid
            self.client.set_options(soapheaders={"EndSession":es})
            self.client.service.Execute({"Statement":None})
            self.sessionid = None
            self.client.set_options(soapheaders=None)

                
XMLAConnection.setupMembers()
