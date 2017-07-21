#!/usr/bin/env python
import sys
import tempfile
import os
from google import search
import argparse
import urllib2
import exiftool

class MetaData:
    def __init__(self, domain, output, limit):
        self.google_basesearch ='site:{} (filetype:doc OR filetype:ppt OR filetype:pps OR filetype:xls OR filetype:docx OR filetype:pptx OR filetype:ppsx OR filetype:xlsx OR filetype:sxw OR filetype:sxc OR filetype:sxi OR filetype:odt OR filetype:ods OR filetype:odg OR filetype:odp OR filetype:pdf OR filetype:wpd OR filetype:svg OR filetype:svgz OR filetype:indd OR filetype:rdp OR filetype:ica)'
        self.outfolder = output
        self.domain = domain
        self.limit = limit
        self.files = []

    def buscar(self):
        print '\033[0;36m' + 'Buscando archivos del dominio {}'.format(self.domain) + '\033[0m'

        if (self.limit is None):
            docs = search(self.google_basesearch.format(self.domain))
        else:
            docs = search(self.google_basesearch.format(self.domain), stop = self.limit)
        #print '\033[0;92' + 'Documento encontrados ' + str(docs.__len__) + '\033[0m'
        for url in docs:
            self.download_file(url)
        if (len(self.files) > 0):
            print '\033[0;93m' + 'Archivos descargados {}'.format(str(len(self.files))) + '\033[0m'
            self.extract_metadata()
        else:
            print '\033[0;31m' + 'No se econtraron archivos relacionados ' + '\033[0m'

    def download_file(self, url):
        try:
            file_name = self.outfolder + '/' + url.split('/')[-1]
            self.files.append(file_name)
            u = urllib2.urlopen(url)
            f = open(file_name, 'wb')
            meta = u.info()
            file_size = int(meta.getheaders("Content-Length")[0])
            print "Descargando: %s Bytes: %s" % (file_name, file_size)

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)
                status = "%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                status = status + chr(8)*(len(status)+1)
                print status,

            f.close()
        except:
            print '\033[0;91m' + 'Error al descargar el archivo {}'.format(url) + '\033[0m'

    def extract_metadata(self):
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata_batch(self.files)
        for d in metadata:
            try:
                print '\033[0;034m' + 'Author : {}'.format(d["PDF:Author"]) + '\033[0m'
            except:
                pass
            


print ('\033[0;92m' + """
=====================================================
__  __  ____  ____   __    ____    __   ____   __   
(  \/  )( ___)(_  _) /__\  (  _ \  /__\ (_  _) /__\  
 )    (  )__)   )(  /(__)\  )(_) )/(__)\  )(  /(__)\ 
(_/\/\_)(____) (__)(__)(__)(____/(__)(__)(__)(__)(__)
======================================================
version: 0.1
author: Daniel Vargas
""" + '\033[0m')

parser = argparse.ArgumentParser(description='Obtiene la informacion de la metada de todos los documentos encontrados')
parser.add_argument('-d','--domain',help='Direccion del dominio', required=True)
parser.add_argument('-o','--output',help='Directorio donde se descargaran los archivos y quedara almacenado el registro.', required=False)
parser.add_argument('-l','--limit',help='Cantidad de registros a buscar', required=False, type=int)
args = parser.parse_args()

if (args.output is None):
    outfolder = tempfile.gettempdir() + '/' + args.domain
else:
    outfolder = args.output

if (not os.path.exists(outfolder)):
    os.makedirs(outfolder);
try:
    metadata = MetaData(args.domain, outfolder, args.limit)
    metadata.buscar()
except KeyboardInterrupt:
    sys.exit(0)
except urllib2.HTTPError as u:
    print '\033[0;91m' + u.reason  + '\033[0m'
except:
    print '\033[0;91m' + str(sys.exc_info()[0]) + '\033[0m'
