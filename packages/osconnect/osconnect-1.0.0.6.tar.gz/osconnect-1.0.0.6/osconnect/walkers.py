# -*- coding: utf-8 -*-
import connect as os_connect
from connect import OsDebug

class OsWalkers(object):
    currentWalker = False

    @staticmethod
    def connectWalker(walker):
        if OsWalkers.currentWalker:
            OsWalkers.currentWalker.disconnect()
        OsWalkers.currentWalker = walker

    @staticmethod
    def makePathToFile(walker, tofile):
        dirs = tofile.split('/')
        k = 1
        pathes = []
        for dir in dirs:
            if k < len(dirs) and len(dir) > 0:
                pathes += [ dir ]
                walker.doCommand('mkdir /' + '/'.join(pathes))
            k += 1

def ifHasElseFalse(mass, name):
    if name in mass:
        return mass[name]
    return False

def WidedDict(dict, wider):
    for w in wider.keys():
        dict[w] = wider[w]
    return dict
    '''
    return {
        'maybe': {
            'password:':self.password,
            'пароль:':self.password,
            }
    }
    '''

class OsWalker(object):
    def __init__(self, command=False, baseWalker=False, connectExpecter=False, connectOnInit=True):
        self.mayDebug = True
        self.command = command
        self.childWalker = False
        self.baseWalker = baseWalker
        self.connectExpecter_ = connectExpecter
        self.lastCommand = ''
        if self.baseWalker:
            self.baseWalker.connectChild(self)
        if connectOnInit:
            self.connect()

    def __del__(self):
        # TODO вообще-то этот код не выполняется
        OsDebug.debug('    *** OsWalker['+self.__class__.__name__+'].__del__ ***', level=0)
        #print '    *** OsWalker['+self.__class__.__name__+'].__del__ ***'
        try:
            self.disconnect()
        except:
            OsDebug.debug('    *** OsWalker['+self.__class__.__name__+'].__del__ ERROR! ***', level=0)
            #print '    *** OsWalker['+self.__class__.__name__+'].__del__ ERROR! ***'

    def setDebug(self, val):
        self.mayDebug = val

    def debug(self, val):
        if self.mayDebug:
            OsDebug.debug(val, level=0)
            #print val

    def connectCommand(self):
        return ''

    def connectExpecter(self):
        if self.connectExpecter_:
            return self.connectExpecter_
        return {
            'need':False,
            'maybe':False
        }

    def disconnectCommand(self):
        return 'exit'

    def connectChild(self, childWalker):
        self.childWalker = childWalker

    def disconnectChild(self):
        if self.childWalker:
            self.childWalker.disconnect()
            self.childWalker = False

    def connect(self, extPexpectSpawn=False):
        self.debug('    *** OsWalker['+self.__class__.__name__+'].connect ***')
        self.disconnectChild()
        disconnectCommand = self.disconnectCommand()
        command = self.command
        if not command:
            command = self.connectCommand()
        if self.baseWalker:
            self.commander = self.baseWalker.commander
            self.connection = self.baseWalker.connection
            self.doCommand(
                command,
                needExpecter=ifHasElseFalse(self.connectExpecter(),'need'),
                maybeExpecter=ifHasElseFalse(self.connectExpecter(),'maybe')
            )
        else:
            self.connection = self.makeConnection(
                command,
                disconnectCommand,
                extPexpectSpawn = extPexpectSpawn
            )
            self.commander = self.connection.getCommander()
        return self

    def makeConnection(self, command, disconnectCommand, extPexpectSpawn=False):
        # если понадобится, чтобы волкер обновременно работал только один, раскомментируй:
        # OsWalkers.connectWalker(self)
        connection = os_connect.OsConnect(
            command,
            disconnectCommand,
            ifHasElseFalse(self.connectExpecter(),'need'),
            ifHasElseFalse(self.connectExpecter(),'maybe'),
            extPexpectSpawn = extPexpectSpawn
        )
        return connection

    def disconnect(self):
        self.debug('    *** OsWalker['+self.__class__.__name__+'].disconnect ***')
        self.disconnectChild()
        if self.baseWalker:
            self.doCommand(self.disconnectCommand())
            self.connection = False
            return
        del self.connection
        try:
            del self.commander
        except:
            self.debug("    !!!!!! NO NEED TO DELETE COMMANDER")

    def isConnected(self):
        try:
            if self.connection:
                return True
        except:
            pass
        return False

    def doCommand(self, command, needExpecter=False, maybeExpecter=False):
        self.lastCommand = command
        self.clearResultMemory()
        if not self.isConnected():
            self.connect()
        else:
            self.disconnectChild()
        if not command:
            return self
        self.debug('    *** OsWalker['+self.__class__.__name__+'].doCommand: '+str(command)+' ***')
        tmp = self.commander.mayDebug
        self.commander.setDebug(self.mayDebug)
        self.commander.doCommand(
            command=command,
            needExpecter=needExpecter,
            maybeExpecter=maybeExpecter
        )
        self.commander.setDebug(tmp)
        return self

    def doPassworedCommand(self, command, password, maybeExpecter=False):
        if not maybeExpecter:
            maybeExpecter = {}
        maybeExpecter['Password:'] = password
        maybeExpecter['Пароль:'] = password
        self.doCommand(
            command = command,
            maybeExpecter = maybeExpecter
        )
        return self
        
    def clearResultMemory(self):
        if OsDebug.tmpfile:
            OsDebug.tmpfile.clearMemory()
    
    def result(self):
        if OsDebug.tmpfile:
            return '\r\n'.join(OsDebug.tmpfile.getMemory())
        else:
            return ''
        
    def resultLines(self):
        return [a.replace('\n','') for a in self.result().split('\r\n') if len(a.replace('\n','')) and self.lastCommand != a and not '#' in a]

class SambaWalker(OsWalker):
    def __init__(self, host, shared_dir, user, password, baseWalker=False):
        self.host = host
        self.shared_dir = shared_dir
        self.user = user
        self.password = password
        self.needExpecterMain = {
            '\>':False,
            'ONLY_ME':True
        }
        super(SambaWalker,self).__init__(False, baseWalker)

    def connectCommand(self):
        return ' '.join([
            'smbclient', '//'+self.host+'/'+self.shared_dir, 
            '-U', self.user, self.password
        ])

    def connectExpecter(self):
        return {
            'maybe': {
                'assword:':self.password,
                'ароль:':self.password,
                '\?':'yes'
            },
            'need': self.needExpecterMain
        }
        
    def putFileToHost(self, file):
        self.doCommand(
            'mput ' + file,
            maybeExpecter = {
                '?:':'y\n',
            }, 
            needExpecter = self.needExpecterMain
        )
        
    def getFileFromHost(self, file):
        self.doCommand(
            'mget ' + file,
            maybeExpecter = {
                '?:':'y\n',
            },
            needExpecter = self.needExpecterMain
        )
        
class SuWalker(OsWalker):
    def __init__(self, user, password, baseWalker=False):
        self.user = user
        self.password = password
        super(SuWalker,self).__init__(False, baseWalker)

    def connectCommand(self):
        return 'su ' + self.user

    def connectExpecter(self):
        return {
            'maybe': {
                'password:':self.password,
                'пароль:':self.password,
            }
        }

class SshWalker(OsWalker):
    def __init__(self, host, user, password, passphrase=False, baseWalker=False):
        self.host = host
        self.user = user
        self.password = password
        self.passphrase = passphrase
        super(SshWalker,self).__init__(False, baseWalker)

    def connectCommand(self):
        return 'ssh '+self.user+'@' + self.host

    def connectExpecter(self):
        dict = {
            'maybe': {
                'password:':self.password,
                'пароль:':self.password,
                '\?':'yes'
            }
        }
        if self.passphrase:
            dict['maybe']['id_rsa\':'] = self.passphrase
        return dict

class SshCopyWalker(OsWalker):
    def __init__(self, fromfile, tofile, password, passphrase=False, baseWalker=False, recursive=False):
        self.fromfile = fromfile
        self.tofile = tofile
        self.password = password
        self.passphrase = passphrase
        self.connectedCopier = False
        self.recursive = recursive
        super(SshCopyWalker,self).__init__(False, baseWalker)

    def connectCommand(self):
        if self.recursive:
            return 'scp -pr '+self.fromfile+' '+self.tofile
        return 'scp '+self.fromfile+' '+self.tofile

    def disconnectCommand(self):
        return False

    def connectExpecter(self):
        dict = {
            'need': {
                '100%':''
            },
            'maybe': {
                'password:':self.password,
                'пароль:':self.password,
                '\?':'yes'
            }
        }
        if self.passphrase:
            dict['maybe']['id_rsa\':'] = self.passphrase
        if self.recursive:
            dict['need'] = {
                '[#\$] ':False,
                'ONLY_ME':True
            }
        return dict

class SshCopier(object):
    def __init__(self, host, user, password, passphrase=False,
                 childSshCopier=False, tempDir=False):
        self.tempDir = tempDir
        self.host = host
        self.user = user
        self.password = password
        self.passphrase = passphrase
        self.childSshCopier = childSshCopier

    def getHostPath(self, file):
        return self.user+'@'+self.host+':'+file

    def getFilePath(self, file):
        if self.tempDir:
            dirs = file.split('/')
            return self.tempDir + dirs[len(dirs)-1]
        return file

    def putFileToHost(self, fromfile, tofile, baseWalker=False, recursive=False):
        if self.childSshCopier:
            topath = self.getFilePath(tofile)
        else:
            topath = tofile
        SshCopyWalker(fromfile, self.getHostPath(topath), self.password,
            passphrase=self.passphrase, baseWalker=baseWalker, recursive=recursive)
        if self.childSshCopier:
            base = SshWalker(self.host, self.user, self.password)
            self.childSshCopier.putFileToHost(topath, tofile, base, recursive=recursive)

    def getFileFromHost(self, fromfile, tofile, baseWalker=False, recursive=False):
        if self.childSshCopier:
            base = SshWalker(self.host, self.user, self.password)
            self.childSshCopier.getFileFromHost(fromfile, tofile, base, recursive=recursive)
            frompath = self.childSshCopier.getFilePath(fromfile)
        else:
            frompath = fromfile
        SshCopyWalker(self.getHostPath(frompath), self.getFilePath(tofile), self.password,
            passphrase=self.passphrase, baseWalker=baseWalker, recursive=recursive)

    def putDirToHost(self, fromdir, todir, baseWalker=False):
        self.putFileToHost(fromdir, todir, baseWalker=baseWalker, recursive=True)

    def getDirFromHost(self, fromdir, todir, baseWalker=False):
        self.getFileFromHost(fromdir, todir, baseWalker=baseWalker, recursive=True)

class RootWalker(OsWalker):
    def __init__(self, command, password):
        self.password = password
        super(RootWalker,self).__init__(command)

    def connectCommand(self):
        return 'su'

    def connectExpecter(self):
        return {
            'maybe': {
                'Password:':self.password,
                'Пароль:':self.password,
                }
        }

class PostgresWalker(OsWalker):
    def __init__(self, command, postgresUser, password):
        self.password = password
        self.postgresUser = postgresUser
        super(PostgresWalker,self).__init__(command)

    def connectCommand(self):
        return 'su ' + self.postgresUser

    def connectExpecter(self):
        return {
            'maybe': {
                'Password:':self.password,
                'Пароль:':self.password,
                }
        }
    def doPassworedCommand(self, command, maybeExpecter=False):
        return super(PostgresWalker,self).doPassworedCommand(command, self.password, maybeExpecter)
        '''
        if not maybeExpecter:
            maybeExpecter = {
                'Password:':self.password,
                'Пароль:':self.password,
            }
        self.doCommand(
            command = command,
            maybeExpecter = maybeExpecter
        )
        '''