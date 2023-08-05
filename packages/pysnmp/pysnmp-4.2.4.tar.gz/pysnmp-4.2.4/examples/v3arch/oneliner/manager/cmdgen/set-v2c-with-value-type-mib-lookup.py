#
# Command Generator
#
# Send SNMP SET request using the following options:
#
# * with SNMPv2c, community 'public'
# * over IPv4/UDP
# * to an Agent at localhost:161
# * setting SNMPv2-MIB::sysName.0 to new value (type taken from MIB)
#
from pysnmp.entity.rfc3413.oneliner import cmdgen

cmdGen = cmdgen.CommandGenerator()

errorIndication, errorStatus, errorIndex, varBinds = cmdGen.setCmd(
    cmdgen.CommunityData('public'),
    cmdgen.UdpTransportTarget(('localhost', 161)),
    (cmdgen.MibVariable('SNMPv2-MIB', 'sysName', 0), 'new system name')
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
