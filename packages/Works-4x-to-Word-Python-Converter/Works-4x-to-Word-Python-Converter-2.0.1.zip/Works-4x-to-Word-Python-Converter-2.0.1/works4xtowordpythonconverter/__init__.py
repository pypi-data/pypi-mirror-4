# -*- coding: utf-8 -*-
from read_works import *
from create import create_docx
import os
from os.path import join
import zipfile
import shutil
import optparse
import sys
from send2trash import send2trash

def parse():
    """Parse any command arguments"""
    parser = optparse.OptionParser()
    parser.add_option('-S', '--sourcePath',
                    action='store',
                    type='string',
                    default='',
                    dest='sourcePath',
                    help='Set the source path to process, if unset defaults to location from which program is run')
    parser.add_option('-D', '--destPath',
                    action='store',
                    type='string',
                    default='',
                    dest='destPath',
                    help='Set the destination path to save processed files to, if unset defaults to saving beside the existing files')
    parser.add_option('--delete',
                    action='store_true',
                    dest='delete',
                    help='Deletes the source files after processing - ARE YOU SURE YOU WANT TO DO THIS?!')
    parser.add_option('-A', '--archive',
                    action='store_true',
                    dest='archive',
                    help='Archive the source files after processing - but doesn\'t delete them, consider using with the dangerous --delete flag')
    parser.add_option('-d', '--debug',
                    action='store_true',
                    dest='debug',
                    help='If called with the --debug flag instead of just warning that a file failed will raise the error so that you can debug it properly - or send problematic file to nick.wilde.90@gmail.com')
    opts, e = parser.parse_args()
    if len(e) > 0:
        parser.print_help()
    return opts, e

def convert(opts):
    filelist = []
    sourcePath = opts.sourcePath
    if not sourcePath: sourcePath = os.path.dirname(__file__)
    srclen = len(sourcePath)
    print "Works-4x-to-Word-Python-Converter running with source path of: %s" % sourcePath
    if opts.destPath:
        if not os.path.isabs(opts.destPath):
            destPath = join(sourcePath,opts.destPath)
        else:
            destPath = opts.destPath
    else: destPath = sourcePath

    if opts.archive:
        archive = zipfile.ZipFile(join(sourcePath,'archive.zip'),mode='w',compression=zipfile.ZIP_DEFLATED)
    else: archive = None

    if opts.delete:
        if not opts.archive:
            confirm = raw_input("WARNING: you have selected the delete source files option, are you sure you want to do this? (enter Y, Yes to continue with delete option active)\n-->")
            if confirm and confirm.lower() in ['y', 'yes']: delete = True
            else: delete = False
        else: delete = True
    else: delete = False
    #scan for source files
    for dir, folders, files in os.walk(sourcePath):
        for file in files:
            if file.endswith('.wps'): #MSWorks WordProcessor File
                filelist.append([dir,file])
    #process files
    for file in filelist:
        src = join(file[0],file[1])
        newfile = join(destPath,file[0][srclen+1:],file[1][:-3]+'docx')
        #read MSWorks file
        text = read_ms_works_file(src)
        props = {} #TODO get proper properties from existing file
        # replace common funky characters (because for some reason* they aren't saved nicely (as in at all))
        # *'some reason' being incomplete unicode compatibility in some of the underlying libs
        for i,line in enumerate(text):
            line = line.replace('\x92',"'") #funkily saved appostrophe
            line = line.replace('\x93','"') #funkily saved open quote
            line = line.replace('\x94','"') #funkily saved close quote
            line = line.replace('\xbe','~') #funkily saved tilde
            line = line.replace('\x85','...') #funkily saved elipses
            line = line.replace('\xe2','~') #unknown char notepad displayed it as an accented a but it was in the middle of a line of tildes so looked best to do this.
            line = line.replace('\xa9','(c)') #copyright symbol
            line = line.replace('\x99','*')
            line = line.replace('\x98','*')
            line = line.replace('\x97','&')
            line = line.replace('\x96','-')
            line = line.replace('\x0b',' ')
            line = line.replace('\x07',' * ')
            line = line.replace('\xb7','*')
            line = line.replace('\xe8','e') #accented e doesn't work
            line = line.replace('\xeb','e') #other accented e doesn't work
            line = line.replace('\x0c','') #unknown whitespace char ???
            if line.find('\x00') != -1:
                line = line.split('\x00')[0] #in case there was trailing junk (only one instance so far found)
            text[i] = line
        #write MS Word 2007 file
        try:
            try: os.makedirs(os.path.dirname(newfile)) #may be needed and quicker to try->except than to check first.
            except: pass
            create_docx(text,newfile,props)
        except:
            print 'Error creating file: ', newfile
            if opts.debug:
                if archive: archive.close() #otherwise the archive created up to this point will be invalid
                raise
            continue
        #unfortunately py-docx doesn't support leading whitespace so **REALLY EXTREMELY NASTY BRUTE FORCE HACK**:
        tmpdir = os.path.join(os.environ['TMP'],'works_to_word')
        if not os.path.exists(tmpdir): os.makedirs(tmpdir)
        with zipfile.ZipFile(newfile) as mydoc:
            mydoc.extractall(tmpdir)
        with open(os.path.join(tmpdir,'word/document.xml')) as f:
            content = f.read()
            content = content.replace(r'<ns0:t>',r'<ns0:t xml:space="preserve">')
            content = content.replace('(c)','©')
        with open(os.path.join(tmpdir,'word/document.xml'), 'w') as f:
            f.write(content)
        with zipfile.ZipFile(newfile,mode='w',compression=zipfile.ZIP_DEFLATED) as docxfile:
            i = len(tmpdir)+1
            for dirpath,dirnames,filenames in os.walk(tmpdir):
                for filename in filenames:
                    templatefile = join(dirpath,filename)
                    archivename = templatefile[i:]
                    docxfile.write(templatefile, archivename)
        shutil.rmtree(tmpdir)
        #Set the modified timestamp to be the same as the original document
        os.utime(newfile,(os.path.getatime(src),os.path.getmtime(src)))
        if archive:
            archive.write(src,src[srclen+1:])
        if delete:
            send2trash(src)
    if archive: archive.close()
    print "Found %i files to process" % len(filelist)

if __name__ == '__main__':
    opts, extra = parse()