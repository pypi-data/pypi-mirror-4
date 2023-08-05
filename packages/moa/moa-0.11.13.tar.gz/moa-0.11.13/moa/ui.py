#!/usr/bin/env python
# Copyright 2009-2011 Mark Fiers
# The New Zealand Institute for Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Licensed under the GPL license (see 'COPYING')
# 
"""
moa.ui
------

communicate information to the user
"""

import os
import re
import sys
import time
import glob
import errno
import shutil
import readline
import traceback
import subprocess
import contextlib

import jinja2.exceptions

import moa.moajinja

import moa.logger as l
from moa.sysConf import sysConf

################################################################################
##
## user interface
##
## Note that anything printed to screen via message, warn, error 
## and exitError automatically is included in the job changemessage
##
################################################################################

FORMAT_CODES_ANSI = {}

for c in sysConf.ansi:
    FORMAT_CODES_ANSI[c] = chr(27) + "["  + sysConf.ansi[c] + "m"
    
FORMAT_CODES_NOANSI = dict([(x,"") for x in FORMAT_CODES_ANSI.keys()])
 
def _appendMessage(status, message):
    """
    Helper function to store messages - for later processing & logging
    """
    if not type(sysConf.autochangemessage) == type([]):
        sysConf.autochangemessage = []
    sysConf.autochangemessage.append(
        (status, fformat(message, f='text', newline = False)))

def _textFormattedMessage(msgs = []):
    """
    text format messages and append automatically generated 
    messages - for logging purposes

    returns a list of lines
    """
    m = []
    for msg in msgs:
        if not msg: continue
        if type(msg) != type([]):
            msg = str(msg).rstrip().split("\n")
        m.extend(msg)
        m.append("")

    if sysConf.autochangemessage:
        if m:
            m.extend(['', '---', '', ''])
        for status, acm in sysConf.autochangemessage:
            if status == 'message':
                m.append(acm)
            else:
                m.append('%s: %s ' % (status, acm))
            m.append('')

    m.append('Command line:')
    m.append('')
    m.append(" ".join(sys.argv))

    while (len(m) > 1) and (not m[0].strip()):
        m = m[1:]
        
    return m
    
    


def exitError(message=''):
    _appendMessage('error', message)
    if sysConf.pluginHandler:
        #see if this is instantiated yet!
        sysConf.pluginHandler.run("post_error")
    if message:
        fprint("{{red}}{{bold}}Error:{{reset}} %s" % message, f='jinja')
    sys.exit(-1)

def exit(message):
    _appendMessage('exit', message)
    fprint("{{green}}Moa:{{reset}}: %s" % message, f='jinja')
    sys.exit(0)

def error(message):
    _appendMessage('error', message)
    fprint("{{red}}{{bold}}Error:{{reset}} %s" % message, f='jinja')

def message(message, store=True):
    if store: 
        _appendMessage('message', message)
    fprint("{{green}}Moa:{{reset}} %s" % message, f='jinja')
    
def warn(message, store=True):
    if store:
        _appendMessage('warn', message)
    fprint("{{blue}}Warning:{{reset}} %s" % message, f='jinja')

def fprint(message, **kwargs):
    sys.stdout.write(fformat(message, **kwargs))
    
def fformat(message, f='text', newline = True, ansi = None):
    
    if f == 'text':
        l.debug("deprecated use of text formatter")

    jenv = None
    if f and  f[:1] == 'j':
        jenv = moa.moajinja.getEnv()

    if ansi == True:
        codes = FORMAT_CODES_ANSI
    elif ansi == False:
        codes = FORMAT_CODES_NOANSI
    else:
        if sys.stdout.isatty() and sysConf.use_ansi:
            codes = FORMAT_CODES_ANSI
        else:
            codes = FORMAT_CODES_NOANSI

    rt = ""

    if not f:
        rt += message
    elif f[0].lower() == 't':
        try:
            rt += message % codes
        except:
            rt += message
    elif f[0].lower() == 'j':
        try:
            template = jenv.from_string(message)
            rt += template.render(**codes)
        except jinja2.exceptions.TemplateSyntaxError:
            rt += message

    if newline:
        rt += "\n"
        
    return rt


################################################################################
##
## readline enabled user prompt
##
#########################################################################

## See if we can do intelligent things with job variables
def untangle(txt):
    return sysConf.job.conf.interpret(txt)
    
## Handle moa directories
_FSCOMPLETECACHE = {}

def fsCompleter(text, state):
    def g(*a):
        #pass
        with open('/tmp/fscomp.%d.log' % os.getuid(), 'a') as F:
            F.write("\t".join(map(str, a)) + "\n")

    g("text   : ", text)
    g("state  :", state)

    if _FSCOMPLETECACHE and text in _FSCOMPLETECACHE.keys():
        try:
            #rv = _FSCOMPLETECACHE[text]
            #g(str(rv))
            rv = _FSCOMPLETECACHE[text][state]
            g('from cache', rv)
            return rv
        except:
            g('%s' % _FSCOMPLETECACHE)
            g('cache problem')
            import traceback
            E = traceback.format_exc()
            g(E)
            return None

    detangle = False
    utext = text
    #see if there are templates in the text - if so - untangle
    if '{{' in text or '{%' in text:
        #do a complete untangle first
        utext = untangle(text)
        g("untang  :", utext)
        detangle = True
        #if utext != text:
        #    detangle = True
    else:
        g("no detangle")

    g("utext : " + utext)
    
    #find the last word - to expand
    #string: stored in 'ctext'. The rest is in 'prefix'
    if ' ' in utext:
        addPrefix = True
        prefix, uptext = utext.rsplit(' ', 1)
    else:
        addPrefix = False
        prefix, uptext = "", utext

    g('prefix :', prefix)
    g('uptext :', uptext)
        
    if os.path.isdir(uptext) and not uptext[-1] == '/': 
        sep = '/'
    else: sep = ''

    
    if prefix or uptext[:2] == './' or \
            uptext[:3] == '../' or uptext[0] == '/':
        #try to expand path
        #get all possibilities
        pos = glob.glob(uptext + sep + '*')
    else:
        #see if there is an executable starting with this
        #
        #seems impossible - cannot call compgen from a script :(
        #cl = ("compgen -c %s" % cutext).split()
        #P = subprocess.Popen(cl, shell=False,
        #                     stdout=subprocess.PIPE,
        #                     stderr=subprocess.PIPE)
        #out, err = P.communicate()
        #print out
        #print err
        pos = []
        
    np = []
    for i, p in enumerate(pos):
        g("found %s" % p)
        if os.path.isdir(p) and not p[-1] == '/':
            p += '/'
        if addPrefix:
            p = prefix + ' ' + p
        if detangle:
            g("detangling")
            g("from %s" % p)
            g("replacing %s" % utext)
            g("with %s" % text)
            p = p.replace(utext , text)
        np.append(p)
    g('pos', np)

    _FSCOMPLETECACHE[text] = np
    g(_FSCOMPLETECACHE)
    try:
        rv = np[state]
        return rv
    except IndexError:
        return None
    
def askUser(prompt, d):
    
    def startup_hook():
        readline.insert_text('%s' % d)
  
    readline.set_completer_delims("\n`~!@#$^&*()-=+[]\|,?")
    readline.set_startup_hook(startup_hook)

    readline.set_completer(fsCompleter)
    readline.parse_and_bind("tab: complete")
    
    vl = raw_input(prompt)

    readline.set_startup_hook() 
    return vl 
    
