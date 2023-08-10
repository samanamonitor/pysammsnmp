from pysnmp.hlapi import *

class SnmpAuth:
    _authProtocol_options = {
        "noauth": usmNoAuthProtocol,
        "md5": usmHMACMD5AuthProtocol,
        "sha1": usmHMACSHAAuthProtocol,
        "sha224": usmHMAC128SHA224AuthProtocol,
        "sha256": usmHMAC192SHA256AuthProtocol,
        "sha384": usmHMAC256SHA384AuthProtocol,
        "sha512": usmHMAC384SHA512AuthProtocol
    }
    _privProtocol_options = {
        "nopriv": usmNoPrivProtocol,
        "des": usmDESPrivProtocol,
        "3des": usm3DESEDEPrivProtocol,
        "aes128": usmAesCfb128Protocol,
        "aes192": usmAesCfb192Protocol,
        "aes256": usmAesCfb256Protocol
    }
    def __init__(self, **kwargs):
        if 'community' in kwargs:
            self.auth = CommunityData(kwargs['community'])
            return

        if 'authKey' not in kwargs or \
            'privKey' not in kwargs or \
            'authProtocol' not in kwargs or \
            'privProtocol' not in kwargs or \
            'userName' not in kwargs:
            raise TypeError("Mandatory parameter missing")

        self._userName = kwargs.get('userName')
        self._authKey = kwargs.get('authKey')
        self._privKey = kwargs.get('privKey')
        self._authProtocol = self._authProtocol_options.get(kwargs.get('authProtocol'))
        self._privProtocol = self._privProtocol_options.get(kwargs.get('privProtocol'))

        if not isinstance(self._userName, str):
            raise TypeError("userName must be str")

        if not isinstance(self._authKey, str):
            raise TypeError("authKey must be str")

        if not isinstance(self._privKey, str):
            raise TypeError("privKey must be str")

        if self._authProtocol is None: 
            raise TypeError("Invalid authProtocol")

        if self._privProtocol is None: 
            raise TypeError("Invalid privProtocol")

        self.auth = UsmUserData(self._userName, authKey=self._authKey, 
            privKey=self._privKey, authProtocol=self._authProtocol, 
            privProtocol=self._privProtocol, securityEngineId=None, 
            authKeyType=usmKeyTypePassphrase, privKeyType=usmKeyTypePassphrase)


class SnmpQuery:
    def __init__(self, hostaddress=None, mib_module_name=None, mib_variable_name_list=None, table=None, port=161, lexicographicMode=False, **kwargs):
        if not isinstance(hostaddress, str):
            raise TypeError("hostaddress must be str")
        if not isinstance(mib_module_name, str):
            raise TypeError("mib_module_name must be str")

        if table is not None and not isinstance(table, str):
            raise TypeError('table must be a str')
        if mib_variable_name_list is not None and not isinstance(mib_variable_name_list, list):
            raise TypeError('mib_variable_name_list must be a list')
        if table is not None and mib_variable_name_list is not None:
            raise TypeError('cannot set table and mib_variable_name_list at the same time')

        self._transport = UdpTransportTarget((hostaddress, port))
        self._identity = SnmpAuth(**kwargs).auth
        self._ctx = ContextData()
        self._engine = SnmpEngine()
        self.mib_module_name = mib_module_name
        self._table = table

        self._lexicographicMode = lexicographicMode
        self._olist = []
        if mib_variable_name_list is not None:
            for v in mib_variable_name_list:
                self._olist += [ObjectType(ObjectIdentity(self.mib_module_name, v))]
        if table is not None:
            self._olist = [ObjectType(ObjectIdentity(self.mib_module_name, table))]

    def __iter__(self):

        self._snmpiter = nextCmd(
            self._engine,
            self._identity,
            self._transport,
            self._ctx,
            *self._olist,
            lexicographicMode= self._lexicographicMode
            )

        if self._table is not None:
            data=[]
            last_key = None
            for self._errorIndication, self._errorStatus, self._errorIndex, self._varBinds in self._snmpiter:
                key = self._varBinds[0][0].getLabel()[-1]
                value = self.__toValue(self._varBinds[0][1])
                if key != last_key:
                    i = 0
                if len(data) <= i:
                    data += [{
                        '_index': self._varBinds[0][0].getMibSymbol()[2][0].prettyPrint()
                    }]
                data[i][key] = value
                last_key = key
                i += 1
            return iter(data)

        else:
            return self

    def __next__(self):
        self._errorIndication, self._errorStatus, self._errorIndex, self._varBinds = next(self._snmpiter)
        data = {
            '_index': self._varBinds[0][0].getMibSymbol()[2][0].prettyPrint()
        }

        for i in range(len(self._varBinds)):
            symbol_label = self._varBinds[i][0].getMibSymbol()[1]
            value = self.__toValue(self._varBinds[i][1])
            data[symbol_label] = value
        return data

    def __toValue(self, data):
        class_name = data.__class__.__name__
        if class_name == "DisplayString":
            return str(data)
        elif class_name == "OctetString":
            return str(data)
        elif class_name == "Counter32":
            return int(data)
        elif class_name == "Counter64":
            return int(data)
        elif class_name == "Integer":
            return int(data)
        elif class_name == "Integer32":
            return int(data)
        elif class_name == "Integer64":
            return int(data)
        elif class_name == "Gauge32":
            return int(data)
        elif class_name == "Gauge64":
            return int(data)
        else:
            return data.prettyPrint()
