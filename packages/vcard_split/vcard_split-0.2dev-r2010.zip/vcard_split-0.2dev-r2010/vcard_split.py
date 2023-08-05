# -*- coding: utf-8 -*-
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

import sys
#import string
import unicodedata
import re
import vobject

import argparse

def toFilename(value):
    if value:
        value = unicode(value)
        value = unicodedata.normalize('NFKD', value)
#        value = unicode(re.sub('[^\w\s@-]', '', value, flags=re.UNICODE).strip())
        value = unicode(re.sub('(?u)[^\w\s@-]', '', value).strip())
#        value = unicode(re.sub('[-\s]+', '_', value, flags=re.UNICODE))
        value = unicode(re.sub('(?u)[-\s]+', '_', value))
    return value

def main():
    parser = argparse.ArgumentParser(
                                     description='Splits one vcard file (*.vcf) to many vcard files\
                                      with one vcard per file. Useful for import contacts to phones, \
                                      thats do not support multiple vcard in one file.'
                                     )
    parser.add_argument('filenames', metavar='filename', type=str, nargs='+', help='filename(s) to process')
    parser.add_argument('-l', '--log-level', help='log details level: DEBUG, INFO, WARNING, ERROR')
    parser.add_argument('-d', '--dummy', action='store_true', help='do not actually write to disk')

    args = parser.parse_args()

    logLevel = args.log_level
    rootLogger = logging.getLogger('')
    if logLevel:
        logLevel = logLevel.upper()
        if logLevel == 'DEBUG': 
            rootLogger.setLevel(logging.DEBUG)
        elif logLevel == 'INFO': 
            rootLogger.setLevel(logging.INFO)
        elif logLevel == 'WARNING': 
            rootLogger.setLevel(logging.WARNING)
        elif logLevel == 'ERROR': 
            rootLogger.setLevel(logging.ERROR)
        else:
            log.warning(u'Unknown log level "%s"' % logLevel)

    log.info(u'Log level: %s' % rootLogger.getEffectiveLevel())
        
    fileCount = 0
    vcardCount = 0
    for filenameIn in args.filenames:
        log.info('Opening file %s...' % filenameIn)
        vcardFileCount = 0
        with open(filenameIn, 'r') as f:
            fileCount += 1 
            for vcard in vobject.readComponents(f, transform=False):
                vcardFileCount += 1
                fields=[]
                if hasattr(vcard, 'fn'):
                    field = toFilename(vcard.fn.value)
                    if field:
                        fields.append(field)
                    else:
                        if hasattr(vcard, 'n'):
                            field = toFilename(vcard.n.value)
                            if field:
                                fields.append(field)
    
                if hasattr(vcard, 'tel'):
                    field = toFilename(vcard.tel.value)
                    if field:
                        fields.append(field)
    
                if hasattr(vcard, 'email'):
                    field = toFilename(vcard.email.value)
                    if field:
                        fields.append(field)
                
                filenameOut = '-'.join(fields)+'.vcf'

                data = vcard.serialize() 
                if args.dummy:
                    log.info('dummy writing file %s...' % filenameOut) 
                else:
                    log.info('writing file %s...' % filenameOut) 
                    with open(filenameOut, 'wb') as fout:
                        fout.write(data)
                        fout.close()

            log.info('Found  %d vcards in file %s' % (vcardFileCount, filenameIn)) 
            vcardCount += vcardFileCount
    print u'Found total %d vcards in %d files' % (vcardCount, fileCount)
if __name__ == '__main__':
    main()