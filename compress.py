import glob
import gzip
import os
import re
import shutil
import sys

# Output file name
MAIN_FILE='static_files_gz.h'
# Matche the name without with extension (no path)
REGEX = '[a-zA-Z0-9]+[.a-zA-Z0-9]+$'

# Convert bytes to C arrays intended to be included in Arduino C/C++ programs.
# MAIN_FILE is the name of the resulting file.
# Subsequent calls appends data to the file.
# Returns the resulting array name.
def buildCArray(mainFile, path, dataBytes):
    # Gera uma lista com a representação textual dos bytes contidos no arquivo
    bytesList = dataBytes.hex(',', 1).split(',')
    textOutput = ''
    entriesPerLine = 20
    count = 0
    for item in bytesList:
        if not count % entriesPerLine:
            textOutput = textOutput + '\n    '
        textOutput = textOutput + f'0x{item:2},'
        count = count + 1

    filename = ''
    with open(mainFile, 'at') as file_out:
        # Array variable name based on the file name and replaces . with _
        # Eliminates trailing . and \ characters
        filename = 'out_' + path.strip('.\\').replace('.', '_')
        filename = filename + ('' if filename.endswith('_gz') else '_gz')
        startDefinition = '\n\nconst byte ' + filename
        startDefinition = startDefinition + '[] PROGMEM = {\n'
        file_out.write(startDefinition)
        file_out.write(textOutput[:-1])
        file_out.write('\n};\n\n')
    return filename

# Compress (gzip) all files (with no .gz extension) found in the
# given directory
def compress(dir):
    for entry in glob.iglob(dir + '/**/*', recursive=True):
        if (os.path.isfile(entry) and not entry.endswith('.gz')):
            print(entry)
            with open(entry, 'rb') as file_in:
                with gzip.open(entry + '.gz', 'wb') as file_out:
                   shutil.copyfileobj(file_in, file_out)

# Creates a file (.h C header) with compressed data from files found in
# the given directory
# The resulting arrays are of type const byte file_name_gz[] PROGMEM = {...};
def toCArray(dir):
    # Cria um novo arquivo ou reescreve se já existir.
    with open(MAIN_FILE, 'wt') as file_out:
        file_out.write('#include <Arduino.h>\n');

    # Run through the files recursively.
    dataMap = []
    for entry in glob.iglob(dir + '/**/*', recursive=True):
        if (os.path.isfile(entry) and not entry.endswith(MAIN_FILE)):
            print(entry)
            filename = re.search(REGEX, entry).group()
            compressed_data = None
            if (entry.endswith('.gz')):
                with gzip.open(entry, 'rb') as file_in:
                    compressed_data = gzip.compress(file_in.read())
            else:
                with open(entry, 'rb') as file_in:
                    compressed_data = gzip.compress(file_in.read())

            # Create the C vector and return its name
            arrayName = buildCArray(MAIN_FILE, filename, compressed_data)
            basePath = sys.argv[2].strip('.\\/')
            urlPath = entry.strip('.').replace('\\', '/')
            urlPath = urlPath.replace(basePath, '')
            dataMap.append({ 
                'path': urlPath[1:] if urlPath[1] == '/' else urlPath,
                'data': arrayName,
                'dataSize': str(len(compressed_data))
            })
    # Builds a map of the resulting variables and their names
    with open(MAIN_FILE, 'at') as file_out:
        textOut = ('\nstruct GzipData {\n'
                   '    const char *path;\n'
                   '    const byte *data;\n'
                   '    const size_t dataSize;\n'
                   '};\n\n'
                   'const struct GzipData gzipDataMap[] = {\n'
                   )
        for data in dataMap:
            textOut = textOut + '    { "' + data['path'] + '", ' + data['data'] + ', ' + data['dataSize'] + ' },\n'

        file_out.write(textOut[:-2] + '\n};')

if __name__ == '__main__':
    if len(sys.argv) == 3:
        if sys.argv[1] == '--compress':
            compress(sys.argv[2])
        elif sys.argv[1] == '--carray':
            toCArray(sys.argv[2])
    else:
        print('Usage: <--compress|--carray> <directory>')
