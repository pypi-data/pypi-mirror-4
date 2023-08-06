import uuid, httplib, time, urllib2
import logging

DEFAULT_APP_ID='QWIN'
DEFAULT_APP_VERSION='2200'
DEFAULT_OFX_VERSION='102'

class Builder:
    def __init__(self, institution, app_id=DEFAULT_APP_ID,app_version=DEFAULT_APP_VERSION,ofx_version=DEFAULT_OFX_VERSION):
        self.institution = institution
        self.app_id = app_id
        self.app_version = app_version
        self.ofx_version = ofx_version
        self.cookie = 3

    def _cookie(self):
        self.cookie += 1
        return str(self.cookie)

    """Generate signon message"""
    def _signOn(self,username=None,password=None):
        i = self.institution
        u = username or i.username
        p = password or i.password
        fidata = [ _field("ORG",i.org) ]
        if i.id:
            fidata += [ _field("FID",i.id) ]
        return _tag("SIGNONMSGSRQV1",
                    _tag("SONRQ",
                         _field("DTCLIENT",_date()),
                         _field("USERID",u),
                         _field("USERPASS",p),
                         _field("LANGUAGE","ENG"),
                         _tag("FI", *fidata),
                         _field("APPID",self.app_id),
                         _field("APPVER",self.app_version),
                         ))

    def _acctreq(self, dtstart):
        req = _tag("ACCTINFORQ",_field("DTACCTUP",dtstart))
        return self._message("SIGNUP","ACCTINFO",req)

# this is from _ccreq below and reading page 176 of the latest OFX doc.
    def _bareq(self, acctid, dtstart, accttype, bankid):
        req = _tag("STMTRQ",
               _tag("BANKACCTFROM",
                   _field("BANKID",bankid),
                    _field("ACCTID",acctid),
                _field("ACCTTYPE",accttype)),
               _tag("INCTRAN",
                   _field("DTSTART",dtstart),
                _field("INCLUDE","Y")))
        return self._message("BANK","STMT",req)
    
    def _ccreq(self, acctid, dtstart):
        req = _tag("CCSTMTRQ",
                   _tag("CCACCTFROM",_field("ACCTID",acctid)),
                   _tag("INCTRAN",
                        _field("DTSTART",dtstart),
                        _field("INCLUDE","Y")))
        return self._message("CREDITCARD","CCSTMT",req)

    def _invstreq(self, brokerid, acctid, dtstart):
        req = _tag("INVSTMTRQ",
                   _tag("INVACCTFROM",
                      _field("BROKERID", brokerid),
                      _field("ACCTID",acctid)),
                   _tag("INCTRAN",
                        _field("DTSTART",dtstart),
                        _field("INCLUDE","Y")),
                   _field("INCOO","Y"),
                   _tag("INCPOS",
                        _field("DTASOF", _date()),
                        _field("INCLUDE","Y")),
                   _field("INCBAL","Y"))
        return self._message("INVSTMT","INVSTMT",req)

    def _message(self,msgType,trnType,request):
        return _tag(msgType+"MSGSRQV1",
                    _tag(trnType+"TRNRQ",
                         _field("TRNUID",_genuuid()),
                         _field("CLTCOOKIE",self._cookie()),
                         request))
    
    def header(self):
        return str.join("\r\n",[ "OFXHEADER:100",
                           "DATA:OFXSGML",
                           "VERSION:%d" % int(self.ofx_version),
                           "SECURITY:NONE",
                           "ENCODING:USASCII",
                           "CHARSET:1252",
                           "COMPRESSION:NONE",
                           "OLDFILEUID:NONE",
                           "NEWFILEUID:"+_genuuid(),
                           ""])

    def authQuery(self, username=None, password=None):
        u = username or self.institution.username
        p = password or self.institution.password
        return str.join("\r\n",[self.header(), _tag("OFX", self._signOn(username=u,password=p))])

    def baQuery(self, acctid, dtstart, accttype, bankid):
        """Bank account statement request"""
        return str.join("\r\n",[self.header(),
                       _tag("OFX",
                                self._signOn(),
                                self._bareq(acctid, dtstart, accttype, bankid))])
                        
    def ccQuery(self, acctid, dtstart):
        """CC Statement request"""
        return str.join("\r\n",[self.header(),
                          _tag("OFX",
                               self._signOn(),
                               self._ccreq(acctid, dtstart))])

    def acctQuery(self,dtstart='19700101000000'):
        return str.join("\r\n",[self.header(),
                          _tag("OFX",
                               self._signOn(),
                               self._acctreq(dtstart))])

    def invstQuery(self, brokerid, acctid, dtstart):
        return str.join("\r\n",[self.header(),
                          _tag("OFX",
                               self._signOn(),
                               self._invstreq(brokerid, acctid,dtstart))])

    def doQuery(self,query):
        logging.info('Builder.doQuery')
        # N.B. urllib doesn't honor user Content-type, use urllib2
        i = self.institution
        garbage, path = urllib2.splittype(i.url)
        host, selector = urllib2.splithost(path)
        h = httplib.HTTPSConnection(host)
        h.request('POST', selector, query, 
                  { "Content-type": "application/x-ofx",
                    "Accept": "*/*, application/x-ofx"
                  })
        res = h.getresponse()
        response = res.read()
        res.close()

        return response
        
def _field(tag,value):
    return "<"+tag+">"+value

def _tag(tag,*contents):
    return str.join("\r\n",["<"+tag+">"]+list(contents)+["</"+tag+">"])

def _date():
    return time.strftime("%Y%m%d%H%M%S",time.localtime())

def _genuuid():
    return uuid.uuid4().hex
