#
# SNMP Devices Simulator
#
# Written by Ilya Etingof <ilya@glas.net>, 2010-2012
#
import os
import stat
import sys
import getopt
if sys.version_info[0] < 3 and sys.version_info[1] < 5:
    from md5 import md5
else:
    from hashlib import md5
import time
if sys.version_info[0] < 3:
    import anydbm as dbm
    from whichdb import whichdb
else:
    import dbm
    whichdb = dbm.whichdb
import bisect
from pyasn1.type import univ
from pyasn1.codec.ber import encoder, decoder
from pyasn1.compat.octets import octs2str, str2octs, int2oct
from pyasn1.error import PyAsn1Error
from pysnmp.entity import engine, config
from pysnmp.entity.rfc3413 import cmdrsp, context
from pysnmp.carrier.asynsock.dgram import udp
try:
    from pysnmp.carrier.asynsock.dgram import udp6
except ImportError:
    udp6 = None
try:
    from pysnmp.carrier.asynsock.dgram import unix
except ImportError:
    unix = None
from pysnmp.carrier.asynsock.dispatch import AsynsockDispatcher
from pysnmp.smi import exval, indices
from pysnmp.proto import rfc1902, rfc1905, api
from pysnmp import error
from pysnmp import debug

# Process command-line options

# Defaults
forceIndexBuild = False
validateData = False
v2cArch = False
v3Only = False
v3User = 'simulator'
v3AuthKey = 'auctoritas'
v3AuthProto = 'MD5'
v3PrivKey = 'privatus'
v3PrivProto = 'DES'
agentUDPv4Address = ('127.0.0.1', 161)
agentUDPv4Endpoints = []
agentUDPv6Endpoints = []
agentUNIXEndpoints = []
deviceDirs = set()
interpolationModules = {}

authProtocols = {
  'MD5': config.usmHMACMD5AuthProtocol,
  'SHA': config.usmHMACSHAAuthProtocol,
  'NONE': config.usmNoAuthProtocol
}

privProtocols = {
  'DES': config.usmDESPrivProtocol,
  '3DES': config.usm3DESEDEPrivProtocol,
  'AES': config.usmAesCfb128Protocol,
  'AES128': config.usmAesCfb128Protocol,
  'AES192': config.usmAesCfb192Protocol,
  'AES256': config.usmAesCfb256Protocol,
  'NONE': config.usmNoPrivProtocol
}
 
helpMessage = 'Usage: %s [--help] [--debug=<category>] [--device-dir=<dir>] [--force-index-rebuild] [--validate-device-data] [--interpolation-module=</path/to/module/file[:args]>] [--agent-udpv4-endpoint=<X.X.X.X:NNNNN>] [--agent-udpv6-endpoint=<[X:X:..X]:NNNNN>] [--agent-unix-endpoint=</path/to/named/pipe>] [--v2c-arch] [--v3-only] [--v3-user=<username>] [--v3-auth-key=<key>] [--v3-auth-proto=<%s>] [--v3-priv-key=<key>] [--v3-priv-proto=<%s>]' % (sys.argv[0], '|'.join(authProtocols), '|'.join(privProtocols))

try:
    opts, params = getopt.getopt(sys.argv[1:], 'h',
        ['help', 'debug=', 'device-dir=', 'force-index-rebuild', 'validate-device-data', 'interpolation-module=', 'agent-address=', 'agent-port=', 'agent-udpv4-endpoint=', 'agent-udpv6-endpoint=', 'agent-unix-endpoint=', 'v2c-arch', 'v3-only', 'v3-user=', 'v3-auth-key=', 'v3-auth-proto=', 'v3-priv-key=', 'v3-priv-proto=']
        )
except Exception:
    sys.stdout.write('%s\r\n%s\r\n' % (sys.exc_info()[1], helpMessage))
    sys.exit(-1)

if params:
    sys.stdout.write('extra arguments supplied %s%s\r\n' % (params, helpMessage))
    sys.exit(-1)

for opt in opts:
    if opt[0] == '-h' or opt[0] == '--help':
        sys.stdout.write('%s\r\n' % helpMessage)
        sys.exit(-1)
    elif opt[0] == '--debug':
        debug.setLogger(debug.Debug(opt[1]))
    elif opt[0] == '--device-dir':
        deviceDirs.add(opt[1])
    elif opt[0] == '--force-index-rebuild':
        forceIndexBuild = True
    elif opt[0] == '--validate-device-data':
        validateData = True
    elif opt[0] == '--interpolation-module':
        args = opt[1].split(':')
        mod, args = args[0], args[1:]
        m = os.path.splitext(os.path.basename(mod))[0]
        if m in interpolationModules:
            sys.stdout.write('interpolation module %s already registered\r\n' %  m)
            sys.exit(-1)
        ctx = { 'path': opt[1],
                'args': args }
        try:
            execfile(mod, ctx)
        except Exception:
            sys.stdout.write('interpolation module %s execution failure: %s\r\n' %  (opt[1], sys.exc_info()[1]))
            sys.exit(-1)
        else:
            interpolationModules[m] = ctx
    elif opt[0] == '--agent-udpv4-endpoint':
        f = lambda h,p=161: (h, int(p))
        try:
            agentUDPv4Endpoints.append(f(*opt[1].split(':')))
        except:
            sys.stdout.write('improper IPv4/UDP endpoint %s\r\n' % opt[1])
            sys.exit(-1)
    elif opt[0] == '--agent-udpv6-endpoint':
        if not udp6:
            sys.stdout.write('This system does not support UDP/IP6\r\n')
            sys.exit(-1)
        if opt[1].find(']:') != -1 and opt[1][0] == '[':
            h, p = opt[1].split(']:')
            try:
                h, p = h[1:], int(p)
            except:
                sys.stdout.write('improper IPv6/UDP endpoint %s\r\n' % opt[1])
                sys.exit(-1)
        elif opt[1][0] == '[' and opt[1][-1] == ']':
            h, p = opt[1][1:-1], 161
        else:
            h, p = opt[1], 161
        agentUDPv6Endpoints.append((h, p))
    elif opt[0] == '--agent-unix-endpoint':
        if not unix:
            sys.stdout.write('This system does not support UNIX domain sockets\r\n')
            sys.exit(-1)
        agentUNIXEndpoints.append(opt[1])
    elif opt[0] == '--agent-address':
        agentUDPv4Address = (opt[1], agentUDPv4Address[1])
    elif opt[0] == '--agent-port':
        agentUDPv4Address = (agentUDPv4Address[0], int(opt[1]))
    elif opt[0] == '--v2c-arch':
        v2cArch = True
    elif opt[0] == '--v3-only':
        v3Only = True
    elif opt[0] == '--v3-user':
        v3User = opt[1]
    elif opt[0] == '--v3-auth-key':
        v3AuthKey = opt[1]
    elif opt[0] == '--v3-auth-proto':
        v3AuthProto = opt[1].upper()
        if v3AuthProto not in authProtocols:
            sys.stdout.write('bad v3 auth protocol %s\r\n' % v3AuthProto)
            sys.exit(-1)
    elif opt[0] == '--v3-priv-key':
        v3PrivKey = opt[1]
    elif opt[0] == '--v3-priv-proto':
        v3PrivProto = opt[1].upper()
        if v3PrivProto not in privProtocols:
            sys.stdout.write('bad v3 privacy protocol %s\r\n' % v3PrivProto)
            sys.exit(-1)

if authProtocols[v3AuthProto] == config.usmNoAuthProtocol and \
    privProtocols[v3PrivProto] != config.usmNoPrivProtocol:
        sys.stdout.write('privacy impossible without authentication\r\n')
        sys.exit(-1)

if not deviceDirs:
    deviceDirs.add('devices')

# for backward compatibility
if not agentUDPv4Endpoints and \
   not agentUDPv6Endpoints and \
   not agentUNIXEndpoints:
    agentUDPv4Endpoints.append(agentUDPv4Address)

# Device file entry parsers

class DumpParser:
    ext = os.path.extsep + 'dump'
    tagMap = {
        '0': rfc1902.Counter32,
        '1': rfc1902.Gauge32,
        '2': rfc1902.Integer32,
        '3': rfc1902.IpAddress,
        '4': univ.Null,
        '5': univ.ObjectIdentifier,
        '6': rfc1902.OctetString,
        '7': rfc1902.TimeTicks,
        '8': rfc1902.Counter32,  # an alias
        '9': rfc1902.Counter64,
    }

    def __nullFilter(value):
        return '' # simply drop whatever value is there when it's a Null
    
    def __unhexFilter(value):
        if value[:5].lower() == 'hex: ':
            value = [ int(x, 16) for x in value[5:].split('.') ]
        elif value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        return value

    filterMap = {
        '4': __nullFilter,
        '6': __unhexFilter
    }

    def parse(self, line): return octs2str(line).split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)

    def evaluateValue(self, oid, tag, value, writeMode=False, origOid=None, origValue=None, deviceFile=None):
        return tag, self.tagMap[tag](
            self.filterMap.get(tag, lambda x: x)(value.strip())
            )
    
    def evaluate(self, line, oidOnly=False, muteValueError=True,
                 writeMode=False, origOid=None, origValue=None,
                 deviceFile=None):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(oid, tag, value, writeMode, origOid, origValue)
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s at %s: %s' % (repr(value), deviceFile, sys.exc_info()[1])
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

class MvcParser(DumpParser):
    ext = os.path.extsep + 'MVC'  # just an alias

class SapParser(DumpParser):
    ext = os.path.extsep + 'sapwalk'  # just an alias
    tagMap = {
        'Counter': rfc1902.Counter32,
        'Gauge': rfc1902.Gauge32,
        'Integer': rfc1902.Integer32,
        'IpAddress': rfc1902.IpAddress,
#        '<not implemented?>': univ.Null,
        'ObjectID': univ.ObjectIdentifier,
        'OctetString': rfc1902.OctetString,
        'TimeTicks': rfc1902.TimeTicks,
        'Counter64': rfc1902.Counter64
    }

    def __stringFilter(value):
        if value[:2] == '0x':
            value = [ int(value[x:x+2], 16) for x in range(2, len(value[2:])+2, 2) ]
        return value

    filterMap = {
        'OctetString': __stringFilter
    }

    def parse(self, line):
        return [ x.strip() for x in octs2str(line).split(',', 2) ]

class WalkParser(DumpParser):
    ext = os.path.extsep + 'snmpwalk'  # just an alias
    # case-insensitive keys as snmpwalk output tend to vary
    tagMap = {
        'OID:': rfc1902.ObjectName,
        'INTEGER:': rfc1902.Integer,
        'STRING:': rfc1902.OctetString,
        'BITS:': rfc1902.Bits,
        'HEX-STRING:': rfc1902.OctetString,
        'GAUGE32:': rfc1902.Gauge32,
        'COUNTER32:': rfc1902.Counter32,
        'COUNTER64:': rfc1902.Counter64,
        'IPADDRESS:': rfc1902.IpAddress,
        'OPAQUE:': rfc1902.Opaque,
        'UNSIGNED32:': rfc1902.Unsigned32,  # this is not needed
        'TIMETICKS:': rfc1902.TimeTicks     # this is made up
    }

    # possible DISPLAY-HINTs parsing should occur here
    def __stringFilter(value):
        if not value:
            return value
        elif value[0] == value[-1] == '"':
            return value[1:-1]
        elif value.find(':') > 0:
            for x in value.split(':'):
                for y in x:
                    if y not in '0123456789ABCDEFabcdef':
                        return value
            return [ int(x, 16) for x in value.split(':') ]
        else:
            return value

    def __opaqueFilter(value):
        return [int(y, 16) for y in value.split(' ')]

    def __bitsFilter(value):
        return ''.join([int2oct(int(y, 16)) for y in value.split(' ')])

    def __hexStringFilter(value):
        return [int(y, 16) for y in value.split(' ')]

    filterMap = {
        'OPAQUE:': __opaqueFilter,
        'STRING:': __stringFilter,
        'BITS:': __bitsFilter,
        'HEX-STRING:': __hexStringFilter
    }

    def parse(self, line):
        oid, value = octs2str(line).strip().split(' = ', 1)
        if oid and oid[0] == '.':
            oid = oid[1:]
        try:
            tag, value = value.split(' ', 1)
        except ValueError:
            # this is implicit snmpwalk's fuzziness
            if value == '""' or value == 'STRING:':
                tag = 'STRING:'
                value = ''
            else:
                tag = 'TimeTicks:'
        return oid, tag.upper(), value

class SnmprecParser:
    ext = os.path.extsep + 'snmprec' 
    tagMap = {}
    for t in ( rfc1902.Gauge32,
               rfc1902.Integer32,
               rfc1902.IpAddress,
               univ.Null,
               univ.ObjectIdentifier,
               rfc1902.OctetString,
               rfc1902.TimeTicks,
               rfc1902.Opaque,
               rfc1902.Counter32,
               rfc1902.Counter64 ):
        tagMap[str(sum([ x for x in t.tagSet[0] ]))] = t

    def parse(self, line): return octs2str(line).strip().split('|', 2)

    def evaluateOid(self, oid):
        return univ.ObjectIdentifier(oid)
    
    def evaluateValue(self, oid, tag, value, writeMode=False, origOid=None, origValue=None, deviceFile=None):
        # Interpolation module reference
        if ':' in tag:
            modName, tag = tag[tag.index(':')+1:], tag[:tag.index(':')]
        else:
            modName = None
        # Unhexify
        if tag[-1] == 'x':
            tag = tag[:-1]
            value = [int(value[x:x+2], 16) for x in  range(0, len(value), 2)]
        if modName:
            if modName in interpolationModules:
                value = interpolationModules[modName]['interpolate'](oid, tag, value, origOid, origValue, deviceFile, writeMode)
            else:
                raise Exception('interpolation module "%s" missing' % modName)
        return tag, self.tagMap[tag](value)

    def evaluate(self, line, oidOnly=False, muteValueError=True, writeMode=False, origOid=None, origValue=None, deviceFile=None):
        oid, tag, value = self.parse(line)
        if oidOnly:
            value = None
        else:
            try:
                tag, value = self.evaluateValue(oid, tag, value, writeMode, origOid, origValue, deviceFile)
            except:
                if muteValueError:
                    value = rfc1902.OctetString(
                        'SIMULATOR VALUE ERROR %s at %s: %s' % (repr(value), deviceFile, sys.exc_info()[1])
                        )
                else:
                    raise
        return self.evaluateOid(oid), value

parserSet = {
    DumpParser.ext: DumpParser(),
    MvcParser.ext: MvcParser(),
    SapParser.ext: SapParser(),
    WalkParser.ext: WalkParser(),
    SnmprecParser.ext: SnmprecParser()
}

class AbstractLayout:
  layout = '?'

# Device text file and OID index

class DeviceFile(AbstractLayout):
    layout = 'text'
    openedQueue = []
    maxQueueEntries = 31  # max number of open text and index files
    def __init__(self, textFile, textParser):
        self.__textFile = textFile
        self.__textParser = textParser
        try:
            self.__dbFile = textFile[:textFile.rindex(os.path.extsep)]
        except ValueError:
            self.__dbFile = textFile

        self.__dbFile = self.__dbFile + os.path.extsep + 'dbm'
    
        self.__db = self.__text = None
        self.__dbType = '?'
        
    def indexText(self, forceIndexBuild=False):
        textFileStamp = os.stat(self.__textFile)[8]

        # gdbm on OS X seems to voluntarily append .db, trying to catch that
        
        indexNeeded = forceIndexBuild
        
        for dbFile in (
            self.__dbFile + os.path.extsep + 'db',
            self.__dbFile
            ):
            if os.path.exists(dbFile):
                if textFileStamp < os.stat(dbFile)[8]:
                    if indexNeeded:
                        sys.stdout.write('Forced index rebuild %s\r\n' % dbFile)
                    elif not whichdb(dbFile):
                        indexNeeded = True
                        sys.stdout.write('Unsupported index format, rebuilding index %s\r\n' % dbFile)
                else:
                    indexNeeded = True
                    sys.stdout.write('Index %s out of date\r\n' % dbFile)
                break
        else:
            indexNeeded = True
            sys.stdout.write('Index does not exist for %s\r\n' % self.__textFile)
            
        if indexNeeded:
            # these might speed-up indexing
            open_flags = 'nfu' 
            while open_flags:
                try:
                    db = dbm.open(self.__dbFile, open_flags)
                except:
                    open_flags = open_flags[:-1]
                    if not open_flags:
                        raise
                else:
                    break

            text = open(self.__textFile, 'rb')

            sys.stdout.write('Indexing device file %s (open flags \"%s\")...' % (self.__textFile, open_flags))
            sys.stdout.flush()
        
            lineNo = 0
            offset = 0
            while 1:
                line = text.readline()
                if not line:
                    break
            
                lineNo += 1

                try:
                    oid, tag, val = self.__textParser.parse(line)
                except Exception:
                    db.close()
                    exc = sys.exc_info()[1]
                    try:
                        os.remove(self.__dbFile)
                    except OSError:
                        pass
                    raise Exception(
                        'Data error at %s:%d: %s' % (
                            self.__textFile, lineNo, exc
                            )
                        )

                if validateData:
                    try:
                        self.__textParser.evaluateOid(oid)
                    except Exception:
                        db.close()
                        exc = sys.exc_info()[1]
                        try:
                            os.remove(self.__dbFile)
                        except OSError:
                            pass
                        raise Exception(
                            'OID error at %s:%d: %s' % (
                                self.__textFile, lineNo, exc
                                )
                            )
                    try:
                        self.__textParser.evaluateValue(oid, tag, val)
                    except Exception:
                        sys.stdout.write(
                            '\r\n*** Error at line %s, value %r: %s\r\n' % \
                            (lineNo, val, sys.exc_info()[1])
                            )

                db[oid] = str(offset)
                offset += len(line)

            text.close()
            db.close()
        
            sys.stdout.write('...%d entries indexed\r\n' % (lineNo - 1,))

        self.__dbType = whichdb(self.__dbFile)

        return self

    def close(self):
        self.__text.close()
        self.__db.close()
        self.__db = self.__text = None
    
    def getHandles(self):
        if self.__db is None:
            if len(DeviceFile.openedQueue) > self.maxQueueEntries:
                DeviceFile.openedQueue[0].close()
                del DeviceFile.openedQueue[0]

            DeviceFile.openedQueue.append(self)

            self.__text = open(self.__textFile, 'rb')
            
            self.__db = dbm.open(self.__dbFile)

        return self.__text, self.__db

    def getTextFile(self): return self.__textFile

    # In-place, by-OID binary search

    def __searchOid(self, oid, eol=str2octs('\n')):
        lo = mid = 0; prev_mid = -1
        self.__text.seek(0, 2)
        hi = sz = self.__text.tell()
        while lo < hi:
            mid = (lo+hi)//2
            self.__text.seek(mid)
            while mid:
                c = self.__text.read(1)
                if c == eol:
                    mid = mid + 1
                    break
                mid = mid - 1    # pivot stepping back in search for full line
                self.__text.seek(mid)
            if mid == prev_mid:  # loop condition due to stepping back pivot
                break
            else:
                prev_mid = mid
            line = self.__text.readline()
            try:
                midval, _ = self.__textParser.evaluate(line, oidOnly=True)
            except Exception:
                raise Exception(
                    'Data error at %s for %s: %s' % (self,oid,sys.exc_info()[1])
                    )                
            if midval < oid:
                lo = mid + len(line)
            elif midval > oid:
                hi = mid
            else:
                return mid
            if mid >= sz:
                return sz
        if lo == mid:
            return lo
        else:
            return hi

    def processVarBinds(self, varBinds, nextFlag=False, writeMode=False):
        rspVarBinds = []

        if nextFlag:
            errorStatus = exval.endOfMib
        else:
            errorStatus = exval.noSuchInstance

        text, db = self.getHandles()
        
        for oid, val in varBinds:
            textOid = str(
                univ.OctetString('.'.join([ '%s' % x for x in oid ]))
                )

            try:
                offset = db[textOid]
                exactMatch = True
            except KeyError:
                if nextFlag:
                    offset = self.__searchOid(oid)
                    exactMatch = False
                else:
                    rspVarBinds.append((oid, errorStatus))
                    continue

            offset = int(offset)

            text.seek(offset)

            line = text.readline()

            if nextFlag and exactMatch:
                line = text.readline()

            if not line:
                rspVarBinds.append((oid, errorStatus))
                continue

            try:
                _oid, _val = self.__textParser.evaluate(line, writeMode=writeMode, origOid=str(oid), origValue=str(val), deviceFile=self.getTextFile())
            except PyAsn1Error:
                _val = errorStatus
            except Exception:
                raise Exception(
                    'Data error at %s for %s: %s' % (self, textOid, sys.exc_info()[1])
                    )

            rspVarBinds.append((_oid, _val))

        return rspVarBinds
 
    def __str__(self):
        return 'file %s, %s-indexed, %s' % (
            self.__textFile, self.__dbType, self.__db and 'opened' or 'closed'
            )

# Collect device files

def getDevices(tgtDir, topLen=None):
    if topLen is None:
        topLen = len(tgtDir.split(os.path.sep))
    dirContent = []
    for dFile in os.listdir(tgtDir):
        fullPath = tgtDir + os.path.sep + dFile
        inode = os.lstat(fullPath)
        if stat.S_ISLNK(inode.st_mode):
            relPath = fullPath.split(os.path.sep)[topLen:]
            fullPath = os.readlink(fullPath)
            if not os.path.isabs(fullPath):
                fullPath = tgtDir + os.path.sep + fullPath
            inode = os.stat(fullPath)
        else:
            relPath = fullPath.split(os.path.sep)[topLen:]
        if stat.S_ISDIR(inode.st_mode):
            dirContent = dirContent + getDevices(fullPath, topLen)
            continue            
        if not stat.S_ISREG(inode.st_mode):
            continue
        try:
            dExt = dFile[dFile.rindex(os.path.extsep):]
        except ValueError:
            continue
        if dExt not in parserSet:
            continue
        dirContent.append(
            (fullPath, parserSet[dExt], os.path.sep.join(relPath)[:-len(dExt)])
            )
    return dirContent

# Lightweignt MIB instrumentation (API-compatible with pysnmp's)

class MibInstrumController:
    def __init__(self, deviceFile):
        self.__deviceFile = deviceFile

    def __str__(self): return str(self.__deviceFile)

    def readVars(self, varBinds, acInfo=None):
        return self.__deviceFile.processVarBinds(varBinds, False)

    def readNextVars(self, varBinds, acInfo=None):
        return self.__deviceFile.processVarBinds(varBinds, True)

    def writeVars(self, varBinds, acInfo=None):
        return self.__deviceFile.processVarBinds(varBinds, False, True)

# Devices index as a MIB instrumentaion at a dedicated SNMP context

class DevicesIndexInstrumController:
    indexSubOid = (1,)
    def __init__(self, baseOid=(1, 3, 6, 1, 4, 1, 20408, 999)):
        self.__db = indices.OidOrderedDict()
        self.__indexOid = baseOid + self.indexSubOid
        self.__idx = 1

    def readVars(self, varBinds, acInfo=None):
        return [ (vb[0], self.__db.get(vb[0], exval.noSuchInstance)) for vb in varBinds ]

    def __getNextVal(self, key, default):
        try:
            key = self.__db.nextKey(key)
        except KeyError:
            return key, default
        else:
            return key, self.__db[key]
                                                            
    def readNextVars(self, varBinds, acInfo=None):
        return [ self.__getNextVal(vb[0], exval.endOfMib) for vb in varBinds ]        

    def writeVars(self, varBinds, acInfo=None):
        return [ (vb[0], exval.noSuchInstance) for vb in varBinds ]        
    
    def addDevice(self, *args):
        for idx in range(len(args)):
            self.__db[
                self.__indexOid + (idx+1, self.__idx)
                ] = rfc1902.OctetString(args[idx])
        self.__idx = self.__idx + 1

devicesIndexInstrumController = DevicesIndexInstrumController()

mibInstrumControllerSet = {
    DeviceFile.layout: MibInstrumController
}

# Suggest variations of context name based on request data
def probeContext(transportDomain, transportAddress, contextName):
    candidate = [
        contextName, '.'.join([ str(x) for x in transportDomain ])
    ]
    if transportDomain[:len(udp.domainName)] == udp.domainName:
        candidate.append(transportAddress[0])
    elif udp6 and transportDomain[:len(udp6.domainName)] == udp6.domainName:
        candidate.append(
            str(transportAddress[0]).replace(':', '_')
        )
    elif unix and transportDomain[:len(unix.domainName)] == unix.domainName:
        candidate.append(transportAddress)

    candidate = [ str(x) for x in candidate if x ]

    while candidate:
        yield rfc1902.OctetString(
                  os.path.normpath(os.path.sep.join(candidate))
              ).asOctets()
        del candidate[-1]
 
if not v2cArch:
    def probeHashContext(self, snmpEngine, stateReference, contextName):
        transportDomain, transportAddress = snmpEngine.msgAndPduDsp.getTransportInfo(stateReference)

        for probedContextName in probeContext(transportDomain, transportAddress, contextName):
            probedContextName = md5(probedContextName).hexdigest()
            try:
                self.snmpContext.getMibInstrum(probedContextName)
            except error.PySnmpError:
                pass
            else:
                return probedContextName
        return contextName

    class GetCommandResponder(cmdrsp.GetCommandResponder):
        def handleMgmtOperation(
                self, snmpEngine, stateReference, contextName, PDU, acInfo
            ):
            cmdrsp.GetCommandResponder.handleMgmtOperation(
                self, snmpEngine, stateReference, 
                probeHashContext(self, snmpEngine, stateReference, contextName),
                PDU, acInfo
            )

    class SetCommandResponder(cmdrsp.SetCommandResponder):
        def handleMgmtOperation(
                self, snmpEngine, stateReference, contextName, PDU, acInfo
            ):
            cmdrsp.SetCommandResponder.handleMgmtOperation(
                self, snmpEngine, stateReference, 
                probeHashContext(self, snmpEngine, stateReference, contextName),
                PDU, acInfo
            )

    class NextCommandResponder(cmdrsp.NextCommandResponder):
        def handleMgmtOperation(
                self, snmpEngine, stateReference, contextName, PDU, acInfo
            ):
            cmdrsp.NextCommandResponder.handleMgmtOperation(
                self, snmpEngine, stateReference, 
                probeHashContext(self, snmpEngine, stateReference, contextName),
                PDU, acInfo
            )

    class BulkCommandResponder(cmdrsp.BulkCommandResponder):
        def handleMgmtOperation(
                self, snmpEngine, stateReference, contextName, PDU, acInfo
            ):
            cmdrsp.BulkCommandResponder.handleMgmtOperation(
                self, snmpEngine, stateReference, 
                probeHashContext(self, snmpEngine, stateReference, contextName),
                PDU, acInfo
            )

# Basic SNMP engine configuration

if v2cArch:
    contexts = { univ.OctetString('index'): devicesIndexInstrumController }
else:
    snmpEngine = engine.SnmpEngine()

    config.addContext(snmpEngine, '')

    snmpContext = context.SnmpContext(snmpEngine)
        
    config.addV3User(
        snmpEngine,
        v3User,
        authProtocols[v3AuthProto], v3AuthKey,
        privProtocols[v3PrivProto], v3PrivKey
        )

if interpolationModules:
    sys.stdout.write('Initializing interpolation modules:\r\n')
    for name, body in interpolationModules.items():
        sys.stdout.write('    %s...  ' % name)
        for x in ('init', 'interpolate', 'shutdown'):
            if x not in body:
                sys.stdout.write('error: missing %s handler!\r\n' % x)
                sys.exit(-1)
        try:
            body['init'](*body['args'])
        except Exception:
            sys.stdout.write('initialization failed: %s\r\n' % sys.exc_info()[1])
            sys.exit(-1)
        else:
            sys.stdout.write('OK\r\n')

# Build pysnmp Managed Objects base from device files information

_mibInstrums = {}

for deviceDir in deviceDirs:
    sys.stdout.write(
        'Scanning "%s" directory for %s data files\r\n%s\r\n' % (deviceDir, ','.join([' *%s' % x.ext for x in parserSet.values()]), '='*66)
    )
    for fullPath, textParser, communityName in getDevices(deviceDir):
        if fullPath in _mibInstrums:
            mibInstrum = _mibInstrums[fullPath]
            sys.stdout.write('Shared device %s\r\n' % (mibInstrum,))
        else:
            deviceFile = DeviceFile(fullPath, textParser).indexText(forceIndexBuild)
            mibInstrum = mibInstrumControllerSet[deviceFile.layout](deviceFile)

            _mibInstrums[fullPath] = mibInstrum
            sys.stdout.write('Device %s\r\n' % (mibInstrum,))

        sys.stdout.write('SNMPv1/2c community name: %s\r\n' % (communityName,))

        if v2cArch:
            contexts[univ.OctetString(communityName)] = mibInstrum
        
            devicesIndexInstrumController.addDevice(
                fullPath, communityName
            )
        else:
            agentName = contextName = md5(univ.OctetString(communityName).asOctets()).hexdigest()

            if not v3Only:
                config.addV1System(
                    snmpEngine, agentName, communityName, contextName=contextName
                )

            snmpContext.registerContextName(contextName, mibInstrum)
                 
            devicesIndexInstrumController.addDevice(
                fullPath, communityName, contextName
            )
                 
            sys.stdout.write('SNMPv3 context name: %s\r\n' % (contextName,))
        
        sys.stdout.write('%s\r\n' % ('-+' * 33,))
        
del _mibInstrums

if v2cArch:
    def getBulkHandler(varBinds, nonRepeaters, maxRepetitions, readNextVars):
        if nonRepeaters < 0: nonRepeaters = 0
        if maxRepetitions < 0: maxRepetitions = 0
        N = min(nonRepeaters, len(varBinds))
        M = int(maxRepetitions)
        R = max(len(varBinds)-N, 0)
        if nonRepeaters:
            rspVarBinds = readNextVars(varBinds[:int(nonRepeaters)])
        else:
            rspVarBinds = []
        if M and R:
            for i in range(N,  R):
                varBind = varBinds[i]
                for r in range(1, M):
                    rspVarBinds.extend(readNextVars((varBind,)))
                    varBind = rspVarBinds[-1]

        return rspVarBinds
 
    def commandResponderCbFun(transportDispatcher, transportDomain,
                              transportAddress, wholeMsg):
        while wholeMsg:
            msgVer = api.decodeMessageVersion(wholeMsg)
            if msgVer in api.protoModules:
                pMod = api.protoModules[msgVer]
            else:
                sys.stdout.write('Unsupported SNMP version %s\r\n' % (msgVer,))
                return
            reqMsg, wholeMsg = decoder.decode(
                wholeMsg, asn1Spec=pMod.Message(),
                )

            communityName = reqMsg.getComponentByPosition(1)
            for communityName in probeContext(transportDomain, transportAddress, communityName):
                if communityName in contexts:
                    break
            else:
                return wholeMsg
            
            rspMsg = pMod.apiMessage.getResponse(reqMsg)
            rspPDU = pMod.apiMessage.getPDU(rspMsg)        
            reqPDU = pMod.apiMessage.getPDU(reqMsg)
    
            if reqPDU.isSameTypeWith(pMod.GetRequestPDU()):
                backendFun = contexts[communityName].readVars
            elif reqPDU.isSameTypeWith(pMod.SetRequestPDU()):
                backendFun = contexts[communityName].writeVars
            elif reqPDU.isSameTypeWith(pMod.GetNextRequestPDU()):
                backendFun = contexts[communityName].readNextVars
            elif hasattr(pMod, 'GetBulkRequestPDU') and \
                     reqPDU.isSameTypeWith(pMod.GetBulkRequestPDU()):
                if not msgVer:
                    sys.stdout.write('GETBULK over SNMPv1 from %s:%s\r\n' % (
                        transportDomain, transportAddress
                        ))
                    return wholeMsg
                backendFun = lambda varBinds: getBulkHandler(varBinds,
                    pMod.apiBulkPDU.getNonRepeaters(reqPDU),
                    pMod.apiBulkPDU.getMaxRepetitions(reqPDU),
                    contexts[communityName].readNextVars)
            else:
                sys.stdout.write('Unsuppored PDU type %s from %s:%s\r\n' % (
                    reqPDU.__class__.__name__, transportDomain,
                    transportAddress
                    ))
                return wholeMsg
    
            varBinds = backendFun(
                pMod.apiPDU.getVarBinds(reqPDU)
                )

            # Poor man's v2c->v1 translation
            errorMap = {  rfc1902.Counter64.tagSet: 5,
                          rfc1905.NoSuchObject.tagSet: 2,
                          rfc1905.NoSuchInstance.tagSet: 2,
                          rfc1905.EndOfMibView.tagSet: 2  }
 
            if not msgVer:
                for idx in range(len(varBinds)):
                    oid, val = varBinds[idx]
                    if val.tagSet in errorMap:
                        varBinds = pMod.apiPDU.getVarBinds(reqPDU)
                        pMod.apiPDU.setErrorStatus(rspPDU, errorMap[val.tagSet])
                        pMod.apiPDU.setErrorIndex(rspPDU, idx+1)
                        break

            pMod.apiPDU.setVarBinds(rspPDU, varBinds)
            
            transportDispatcher.sendMessage(
                encoder.encode(rspMsg), transportDomain, transportAddress
                )
            
        return wholeMsg

    # Configure access to devices index
    
    contexts['index'] = devicesIndexInstrumController
    
    # Configure socket server
   
    sys.stdout.write('Listening at:\r\n')
 
    transportDispatcher = AsynsockDispatcher()
    for idx in range(len(agentUDPv4Endpoints)):
        transportDispatcher.registerTransport(
                udp.domainName + (idx,),
                udp.UdpTransport().openServerMode(agentUDPv4Endpoints[idx])
            )
        sys.stdout.write('  UDP/IPv4 endpoint %s:%s, transport ID %s\r\n' % (agentUDPv4Endpoints[idx] + ('.'.join([str(x) for x in udp.domainName + (idx,)]),)))
    for idx in range(len(agentUDPv6Endpoints)):
        transportDispatcher.registerTransport(
                udp6.domainName + (idx,),
                udp6.Udp6Transport().openServerMode(agentUDPv6Endpoints[idx])
            )
        sys.stdout.write('  UDP/IPv6 endpoint %s:%s, transport ID %s\r\n' % (agentUDPv6Endpoints[idx] + ('.'.join([str(x) for x in udp6.domainName + (idx,)]),)))
    for idx in range(len(agentUNIXEndpoints)):
        transportDispatcher.registerTransport(
                unix.domainName + (idx,),
                unix.UnixTransport().openServerMode(agentUNIXEndpoints[idx])
            )
        sys.stdout.write('  UNIX domain endpoint %s, transport ID %s\r\n' % (agentUNIXEndpoints[idx], '.'.join([str(x) for x in unix.domainName + (idx,)])))
    transportDispatcher.registerRecvCbFun(commandResponderCbFun)
else:
    sys.stdout.write('SNMPv3 credentials:\r\nUsername: %s\r\n' % v3User)
    if authProtocols[v3AuthProto] != config.usmNoAuthProtocol:
        sys.stdout.write('Authentication key: %s\r\nAuthentication protocol: %s\r\n' % (v3AuthKey, v3AuthProto))
        if privProtocols[v3PrivProto] != config.usmNoPrivProtocol:
            sys.stdout.write('Encryption (privacy) key: %s\r\nEncryption protocol: %s\r\n' % (v3PrivKey, v3PrivProto))

    # Configure access to devices index

    config.addV1System(snmpEngine, 'index',
                       'index', contextName='index')

    snmpContext.registerContextName(
        'index', devicesIndexInstrumController
        )

    # Configure socket server

    sys.stdout.write('Listening at:\r\n')

    for idx in range(len(agentUDPv4Endpoints)):
        config.addSocketTransport(
            snmpEngine,
            udp.domainName + (idx,),
            udp.UdpTransport().openServerMode(agentUDPv4Endpoints[idx])
        )
        sys.stdout.write('  UDP/IPv4 endpoint %s:%s, transport ID %s\r\n' % (agentUDPv4Endpoints[idx] + ('.'.join([str(x) for x in udp.domainName + (idx,)]),)))
    for idx in range(len(agentUDPv6Endpoints)):
        config.addSocketTransport(
            snmpEngine,
            udp6.domainName + (idx,),
            udp6.Udp6Transport().openServerMode(agentUDPv6Endpoints[idx])
        )
        sys.stdout.write('  UDP/IPv6 endpoint %s:%s, transport ID %s\r\n' % (agentUDPv6Endpoints[idx] + ('.'.join([str(x) for x in udp6.domainName + (idx,)]),)))
    for idx in range(len(agentUNIXEndpoints)):
        config.addSocketTransport(
            snmpEngine,
            unix.domainName + (idx,),
            unix.UnixTransport().openServerMode(agentUNIXEndpoints[idx])
        )
        sys.stdout.write('  UNIX domain endpoint %s, transport ID %s\r\n' % (agentUNIXEndpoints[idx], '.'.join([str(x) for x in unix.domainName + (idx,)])))

    # SNMP applications

    GetCommandResponder(snmpEngine, snmpContext)
    SetCommandResponder(snmpEngine, snmpContext)
    NextCommandResponder(snmpEngine, snmpContext)
    BulkCommandResponder(snmpEngine, snmpContext)

    transportDispatcher = snmpEngine.transportDispatcher

# Run mainloop

transportDispatcher.jobStarted(1) # server job would never finish

# Python 2.4 does not support the "finally" clause

exc_info = None

try:
    transportDispatcher.runDispatcher()
except KeyboardInterrupt:
    sys.stdout.write('Process terminated\r\n')
except Exception:
    exc_info = sys.exc_info()

if interpolationModules:
    sys.stdout.write('Shutting down interpolation modules:\r\n')
    for name, body in interpolationModules.items():
        sys.stdout.write('    %s...  ' % name)
        try:
            body['shutdown'](*body['args'])
        except Exception:
            sys.stdout.write('shutdown failed: %s\r\n' % sys.exc_info()[1])
        else:
            sys.stdout.write('OK\r\n')

transportDispatcher.closeDispatcher()

if exc_info:
    raise exc_info[1]
