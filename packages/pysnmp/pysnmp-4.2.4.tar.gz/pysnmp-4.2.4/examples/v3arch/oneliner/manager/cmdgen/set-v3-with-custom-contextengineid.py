#
# Command Generator
#
# Send SNMP GET request using the following options:
#
# * with SNMPv3 with user 'usr-md5-des', MD5 auth and DES privacy protocols
# * use remote SNMP Engine ID 0x8000000004030201 (USM autodiscovery will run)
# * over IPv4/UDP
# * to an Agent at localhost:161
# * setting SNMPv2-MIB::sysName.0 to new value (type taken from MIB)
#
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902

cmdGen = cmdgen.CommandGenerator()

errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
    cmdgen.UsmUserData(
        'usr-md5-des', 'authkey1', 'privkey1',
        contextEngineId=rfc1902.OctetString(hexValue='8000000004030201')
    ),
    cmdgen.UdpTransportTarget(('localhost', 161)),
    (cmdgen.MibVariable('SNMPv2-MIB', 'sysName', 0), 'new system name'),
)

# Check for errors and print out results
if errorIndication:
    print(errorIndication)
else:
    if errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex)-1] or '?'
            )
        )
    else:
        for name, val in varBinds:
            print('%s = %s' % (name.prettyPrint(), val.prettyPrint()))
