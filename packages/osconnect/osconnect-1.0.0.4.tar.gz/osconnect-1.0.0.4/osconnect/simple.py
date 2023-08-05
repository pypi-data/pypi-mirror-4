# -*- coding: utf-8 -*-
import pexpect, sys, subprocess

def getSubprocess(command, **params):
    return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, **params)

def simpleCommand(command, **params):
    return getSubprocess(command, **params).stdout.read()
    
def simpleCommandLines(command, **params):
    return getSubprocess(command, **params).stdout.readlines()

def tryCommand(command, **params):
    try:
        subprocess.check_call(command, shell=True, stdout=subprocess.PIPE, **params)
        #lines = getSubprocess(command, **params).stdout.readlines()
        return True
    except:
        return False