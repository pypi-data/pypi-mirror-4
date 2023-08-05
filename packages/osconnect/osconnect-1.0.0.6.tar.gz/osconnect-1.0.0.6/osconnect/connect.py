# -*- coding: utf-8 -*-
import pexpect, sys, subprocess

class OsKeyControl(object):
    def __init__(self, key):
        self.key = key

class OsDebugWriter(object):
    def __init__(self, filename=False):
        if filename:
            self.file = open(filename, 'w')
        else:
            self.file = False
        self.printable = False

    def write(self, *args, **kwargs):
        print 'WRITE:', args
        for a in args:
            if ('ERROR' in a) or ('error' in a) or self.printable:
                print ' '.join(args)
        if self.file:
            self.file.write(*args, **kwargs)

    def flush(self, *args, **kwargs):
        print 'FLUSH:', args
        if self.file:
            self.file.flush(*args, **kwargs)
            
    def clearMemory(self):
        pass
    
    def getMemory(self):
        return []
            
class OsDebugMemory(OsDebugWriter):
    def __init__(self):
        super(OsDebugMemory, self).__init__(False)
        self.memory = []

    def write(self, *args, **kwargs):
        self.memory += [args[0],]

    def flush(self, *args, **kwargs):
        #print 'FLUSH:', args
        pass
    
    def clearMemory(self):
        self.memory = []
        
    def getMemory(self):
        return self.memory
    

class OsDebug(object):
    LEVELS = {
        'EXPECTER': 0,
        'COMMANDER': 1,
        'CONNECT': 2,
    }

    debugParams = {
        'level': 8
    }

    tmpfile = False
    
    @staticmethod
    def setPrintable(val=True):
        if OsDebug.tmpfile:
            OsDebug.tmpfile.printable = val

    @staticmethod
    def connectToTmpFile():
        OsDebug.tmpfile = OsDebugWriter('/tmp/os_debug.tmp')
        
    @staticmethod
    def connectToNulFile():
        OsDebug.tmpfile = OsDebugWriter(False)
        
    @staticmethod
    def connectToMemory():
        OsDebug.tmpfile = OsDebugMemory()

    @staticmethod
    def logfile():
        if OsDebug.tmpfile:
            return OsDebug.tmpfile
        return sys.stdout

    @staticmethod
    def setLevel(level):
        OsDebug.debugParams['level'] = level
        
    @staticmethod
    def getLevel():
        return OsDebug.debugParams['level']

    @staticmethod
    def debug(*args, **kwargs):
        if 'level' in kwargs:
            level = kwargs['level']
        else:
            level = 0
        if level >= OsDebug.debugParams['level']:
            print ' '.join([str(a) for a in args])

class QuestsAnswersObject(object):
    def __init__(self, mass):
        if not mass:
            self.quests = []
            self.answers = []
            self.needOnlyMe = False
            return
        self.quests = []
        self.answers = []
        self.needOnlyMe = False
        for quest in mass.keys():
            if quest == 'ONLY_ME':
                if mass[quest]:
                    self.needOnlyMe = True
            else:
                self.quests += [quest]
                self.answers += [mass[quest]]
            
'''
def getQuestsAndAnswers(mass):
    if not mass:
        return [], [], False
    quests = []
    answers = []
    needOnlyMe = False
    for quest in mass.keys():
        if quest == 'ONLY_ME':
            if mass[quest]:
                needOnlyMe = True
        else:
            quests += [quest]
            answers += [mass[quest]]
    return quests, answers, needOnlyMe
'''
    
class NeedTester(object):
    def __init__(self, needObject = False, maybeObject = False):
        self.needObject = needObject
        self.maybeObject = maybeObject
        count = len(needObject.quests)
        self.needBoolStart = 1 + len(maybeObject.quests)
        self.massive = []
        self.fin = False
        if count:
            k = count
            while k > 0:
                self.massive += [False,]
                k -= 1
            self.needMe = True
            self.appendNeedToMaybe()
        else:
            self.needMe = False
            
    def appendNeedToMaybe(self):
        self.maybeObject.quests += self.needObject.quests
        self.maybeObject.answers += self.needObject.answers
            
    def setChecked(self, i):
        self.massive[i] = True
    def isFilled(self):
        for m in self.massive:
            if not m:
                return False
        return True
    def setCheckedByExpect(self, i):
        pos = i - self.needBoolStart
        if pos >= 0:
            self.setChecked(pos)
    def execute(self, i):
        if self.needMe:
            self.setCheckedByExpect(i)
            if self.isFilled():
                if self.needObject.needOnlyMe:
                    self.fin = True
                    return self
                self.needMe = False
        if i == 0:
            self.fin = True
        return self
        

class OsExpecter(object):
    def __init__(self, child, commander=False):
        self.expecter = "[#\$] "
        self.child = child
        self.commander = commander
        if commander and not commander.expecter:
            commander.expecter = self
        self.mayDebug = True

    def setDebug(self, val):
        self.mayDebug = val

    def doExpect(self, exp):
        self.debugIfMay('    +++ expect start:', str(exp), '+++', level=0)
        i = self.child.expect(exp, timeout=None)
        self.debugIfMay('\n    +++ expect finded:', str(exp[i]), '+++', level=0)
        return i
        
    def debugIfMay(self, *args, **kwargs):
        if self.mayDebug:
            OsDebug.debug(*args, **kwargs)

    def expect(self, needExpecter=False, maybeExpecter=False):
        needTester = NeedTester(
            needObject = QuestsAnswersObject(needExpecter),
            maybeObject = QuestsAnswersObject(maybeExpecter)
        )
        self.expectWhile(needTester)
        
    def expectWhile(self, needTester):
        while True:
            i = self.doExpect([self.expecter,] + needTester.maybeObject.quests)
            if needTester.execute(i).fin:
                return
            answer = needTester.maybeObject.answers[i-1]
            if answer:
                self.commander.sendCommand(answer)
            else:
                self.tryExpect(needTester.needObject.quests)
                return

    def tryExpect(self, needQuests=[]):
        try:
            exp = self.expecter
            i = self.doExpect([exp,] + needQuests)
        except:
            pass

class OsCommander(object):
    def __init__(self, child, expecter=False):
        self.expecter = expecter
        if expecter and not expecter.commander:
            expecter.commander = self
        self.child = child
        self.mayDebug = True

    def setDebug(self, val):
        self.mayDebug = val
        self.expecter.setDebug(val)
        
    def debugIfMay(self, *args, **kwargs):
        if self.mayDebug:
            OsDebug.debug(*args, **kwargs)

    '''
    def sendCommand(self, command):
        self.debugIfMay("    *** OsCommander.sendCommand:", command, "***", level=0)
        self.child.sendline(command)
    '''
        
    def sendCommand(self, command):
        self.debugIfMay("    *** OsCommander.sendCommand:", command, "***", level=0)
        if command.__class__.__name__ == 'OsKeyControl':
            self.child.sendcontrol(command.key)
        else:
            self.child.sendline(command)

    def doCommand(self, command, needExpecter=False, maybeExpecter=False):
        self.debugIfMay("    *** OsCommander.doCommand:", command, "***", level=0)
        if command:
            self.sendCommand(command)
        self.expecter.expect(needExpecter, maybeExpecter)

class OsConnect(object):
    def __init__(self, command, disconnectCommand, needExpecter, maybeExpecter, extPexpectSpawn=False):
        self.disconnectCommand = disconnectCommand
        self.connect(
            command, needExpecter, maybeExpecter, extPexpectSpawn
        )

    def __del__(self):
        self.disconnect()

    def getCommander(self):
        return self.osCommander

    def connect(self, command, needExpecter, maybeExpecter, extPexpectSpawn=False):
        if extPexpectSpawn:
            child = self.sendConnect(command, pexpectSpawn=extPexpectSpawn)
        else:
            child = self.sendConnect(command)
        self.osCommander = OsCommander(child, False)
        expecter = OsExpecter(child, self.osCommander)
        self.osCommander.expecter = expecter
        expecter.expect(needExpecter, maybeExpecter)
        return child, expecter

    def sendConnect(self, command, pexpectSpawn=pexpect.spawn):
        OsDebug.debug("    *** OsConnectPrivate.sendConnect:", command, "***", level=0)
        self.child = pexpectSpawn(command)
        self.child.logfile = OsDebug.logfile()
        return self.child

    def disconnect(self):
        OsDebug.debug("    *** OsConnectPrivate.disconnect ***", level=0)
        self.osCommander.doCommand(
            self.disconnectCommand,
            maybeExpecter={pexpect.EOF:False}
        )

