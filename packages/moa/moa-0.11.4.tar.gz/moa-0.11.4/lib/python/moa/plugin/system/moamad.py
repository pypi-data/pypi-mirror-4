# Copyright 2009-2011 Mark Fiers
# The New Zealand Institute for Plant & Food Research
# 
# This file is part of Moa - http://github.com/mfiers/Moa
# 
# Licensed under the GPL license (see 'COPYING')
# 
"""
**moamad** - add mad metadata to files
--------------------------------------
"""

import os
import sys
import hashlib
import socket
from datetime import datetime
import subprocess as sp

from madpy.metadata import Metadata

import moa.ui
import moa.args
import moa.utils
import moa.logger
from moa.sysConf import sysConf

l = moa.logger.getLogger(__name__)

def _get_hash(hash_type, filename):
    """
    Generate a hash for a file 
    """
    process = sp.Popen([hash_type, filename], stdout=sp.PIPE)
    out = process.communicate()[0]
    hashstring = out.strip().split()[0]
    return hashstring

def _get_uri(filename):
    hostname = socket.gethostname()
    fullfilename = os.path.abspath(os.path.expanduser(filename))
    uri = "ssh://%s%s" % (hostname, fullfilename)
    return uri

def hook_finish():
    for inputs, outputs in sysConf.actor.files_processed:
        for filename in outputs:
            mdf = Metadata(filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(filename)).isoformat()
            uri = _get_uri(filename)
            metadata = {}
            metadata['LastModified'] = mtime
            metadata['FileSize'] = os.path.getsize(filename)
            metadata['Sha1sum'] = _get_hash('sha1sum', filename)
            metadata['Uri'] = uri
            
            mdf.update(metadata)
            mdf.save()

            
        
        #moa.sysConf.actor
#     job = sysConf.job
#     job.data.mappedSets = {}
#     fss = job.data.filesets
#     #first find the 'sets & singletons'
#     for fsid in fss.keys():
#         fs = fss[fsid]
#         if fs.type == 'set':
#             job.data.mappedSets[fsid] = {
#                 'type': 'group',
#                 'fs' : fs,
#                 'lifs': _prepFileList(fs.files),
#                 'maps' : {}}
#         elif fs.type == 'single':
#             job.data.mappedSets[fsid] = {
#                 'type': 'single',
#                 'lifs': _prepFileList(fs.files),
#                 'fs' : fs }
# --
            
#     #now find the maps that map to the other sets
#     for fsid in fss.keys():
#         fs = fss[fsid]
#         if fs.type == 'map':
#             source = fs.source
#             fs['lifs'] = _prepFileList(fs.files)
#             job.data.mappedSets[source]['maps'][fsid] = fs

# def _preformatFile(f):
#     """
#     Check if a file exists
#     """
#     if os.path.isfile(f):
#         return "{{green}}%s{{reset}}" % f
#     else:
#         return "{{red}}%s{{reset}}" % f


# @moa.args.doNotLog
# @moa.args.needsJob
# @moa.args.command
# def files(job, args):
#     """
#     Show in and output files for this job

#     Display a list of all files discovered (for input & prerequisite
#     type filesets) and inferred from these for map type filesets.
    
#     """
    
#     filesets = job.template.filesets.keys()
#     filesets.sort()
#     #first print singletons
#     fsets = []
#     fmaps = []
#     for fsid in filesets:
#         templateInfo = job.template.filesets[fsid]
#         files = job.data.filesets[fsid].files

#         if templateInfo.type == 'set':
#             fsets.append(fsid)
#             continue
#         elif templateInfo.type == 'map':
#             fmaps.append(fsid)
#             continue
#         if len(files) == 0:
#             moa.ui.fprint(
#                 ('* Fileset: %%(bold)s%-20s%%(reset)s (single): ' +
#                  '%%(bold)s%%(red)sNo file found%%(reset)s') % fsid )
#         elif len(files) == 1:
#             moa.ui.fprint(
#                 '* Fileset: {{bold}}%-20s{{reset}} (single)\n' % fsid,
#                 f='jinja')
#             moa.ui.fprint('   ' + _preformatFile(files[0]), f='jinja')

#     if len(fsets + fmaps) == 0:
#         return
    
#     #rearrange the files into logical sets
#     nofiles = len(job.data.filesets[(fsets + fmaps)[0]].files) 
#     moa.ui.fprint("")
   
#     for i in range(min(5, nofiles)):
#         thisSet = []
#         for j, fsid in enumerate((fsets + fmaps)):
#             files = job.data.filesets[fsid].files
#             templateInfo = job.template.filesets[fsid]
#             thisSet.append((templateInfo.category,
#                             templateInfo.type,
#                             fsid,
#                             files[i]))
#             if j == 0:
#                 moa.ui.fprint("  {{bold}}%3d{{reset}}:" % i, f='jinja', newline=False)
#             else:
#                 moa.ui.fprint("      ", f='jinja', newline=False)
#             cat = templateInfo.category
#             if cat == 'input':
#                 moa.ui.fprint("{{green}}inp{{reset}}", f='jinja', newline=False)
#             elif cat == 'output':
#                 moa.ui.fprint("{{blue}}out{{reset}}", f='jinja', newline=False)
#             else:
#                 moa.ui.fprint("{{red}}%s{{reset}}" % cat[:3], f='jinja', newline=False)
#             moa.ui.fprint(" {{gray}}%-5s{{reset}}" % templateInfo.type, f='jinja', newline=False)
#             moa.ui.fprint(" {{bold}}%-20s{{reset}} " % fsid, f='jinja', newline=False)
#             moa.ui.fprint(_preformatFile(files[i]), f='jinja', newline=False)
#             moa.ui.fprint("")
#         moa.ui.fprint("")
