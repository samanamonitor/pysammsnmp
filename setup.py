from setuptools import setup, find_packages
from sammsnmp import __version__
from glob import glob
import re

def set_control_version():
    with open("./debian/control.tmpl", "r") as src, open("./debian/control", "w") as dst:
        while True:
            datain = src.readline()
            if len(datain) == 0: break
            dataout = re.sub(r"%VERSION%", __version__, datain)
            dst.write(dataout)

if __name__ == "__main__":
    set_control_version()
    setup(
        name='sammsnmp',
        version=__version__,
        packages=find_packages(include=['sammsnmp', 'sammsnmp.*']),
        data_files=[('/usr/share/snmp/mibs/', glob('support/snmp/mibs/*') )],
        install_requires=[ 'easysnmp' ]
    )
