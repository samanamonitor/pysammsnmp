from easysnmp import Session

class SnmpQuery:
    def __init__(self, mib_variable_name_list=None, table=None, **kwargs):
        self._table = None
        self._mib_variable_name_list = None
        self._data = None
        self.session = None

        if table is not None:
            if not isinstance(table, str):
                raise TypeError('table must be a str')
            self._table = table

        if mib_variable_name_list is not None:
            if not isinstance(mib_variable_name_list, list):
                raise TypeError('mib_variable_name_list must be a list')
            self._mib_variable_name_list = mib_variable_name_list

        if self._table is not None and self._mib_variable_name_list is not None:
            raise TypeError('cannot set table and mib_variable_name_list at the same time')

        self.session = Session(**kwargs)

    def __iter__(self):
        self._data={}

        if self._table is not None:
            data = self.session.walk(self._table)
        elif self._mib_variable_name_list is not None:
            data = self.session.get_bulk(self._mib_variable_name_list, 
                non_repeaters=len(self._mib_variable_name_list))

        for i in data:
            if i.oid_index == '':
                try:
                    entry, unknown_oid, oid_index = i.oid.split('.', 2)
                    oid = "%s.%s" % (entry, unknown_oid)
                except:
                    continue
            else:
                oid_index = i.oid_index
                oid = i.oid

            value = None
            try:
                value = int(i.value)
            except ValueError:
                try:
                    value = float(i.value)
                except ValueError:
                    value = i.value

            self._data.setdefault(oid_index, {})[oid] =  value

        self._snmpiter = iter(self._data.items())
        return self

    def __next__(self):
        return next(self._snmpiter)[1]

