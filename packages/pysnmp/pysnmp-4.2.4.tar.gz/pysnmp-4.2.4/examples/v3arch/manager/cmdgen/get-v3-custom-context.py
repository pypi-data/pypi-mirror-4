#
# GET Command Generator
#
# Send a SNMP GET request
#     with SNMPv3 with user 'usr-md5-none', SHA auth and no privacy protocols
#     for MIB instance identified by contextEngineId: 8000000001020304,
#                                    contextName: my-context
#     over IPv4/UDP
#     to an Agent at 127.0.0.1:161
#     for an OID in tuple form
#
# This script performs similar to the following Net-SNMP command:
#
# $ snmpget -v3 -l authNoPriv -u usr-md5-none -A authkey1 -E 8000000001020304 -n my-context -ObentU 127.0.0.1:161  1.3.6.1.2.1.1.1.0
#
from pysnmp.entity import engine, config
from pysnmp.carrier.asynsock.dgram import udp
from pysnmp.entity.rfc3413 import cmdgen
from pysnmp.proto import rfc1902

# Create SNMP engine instance
snmpEngine = engine.SnmpEngine()

#
# SNMPv3/USM setup
#

# user: usr-md5-none, auth: MD5, priv: NONE
config.addV3User(
    snmpEngine, 'usr-md5-none',
    config.usmHMACMD5AuthProtocol, 'authkey1'
)
config.addTargetParams(snmpEngine, 'my-creds', 'usr-md5-none', 'authNoPriv')

#
# Setup transport endpoint and bind it with security settings yielding
# a target name (choose one entry depending of the transport needed).
#

# UDP/IPv4
config.addSocketTransport(
    snmpEngine,
    udp.domainName,
    udp.UdpSocketTransport().openClientMode()
)
config.addTargetAddr(
    snmpEngine, 'my-router',
    udp.domainName, ('127.0.0.1', 161),
    'my-creds'
)

# Error/response reciever
def cbFun(sendRequestHandle,
          errorIndication, errorStatus, errorIndex,
          varBindTable, cbCtx):
    if errorIndication:
        print(errorIndication)
    elif errorStatus:
        print('%s at %s' % (
            errorStatus.prettyPrint(),
            errorIndex and varBindTable[-1][int(errorIndex)-1] or '?'
            )
        )
    else:
        for oid, val in varBindTable:
            print('%s = %s' % (oid.prettyPrint(), val.prettyPrint()))

# Prepare and send a request message, pass custom ContextEngineId & ContextName
cmdgen.GetCommandGenerator().sendReq(
    snmpEngine,
    'my-router',
    ( ((1,3,6,1,2,1,1,1,0), None), ),
    cbFun,
    contextEngineId=rfc1902.OctetString(hexValue='8000000001020304'),
    contextName=rfc1902.OctetString('my-context')
)

# Run I/O dispatcher which would send pending queries and process responses
snmpEngine.transportDispatcher.runDispatcher()
