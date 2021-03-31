# Gzip data to C arrays
Generate C arrays (gzipped)  from files.

## Motivation
This script is intended to use for compression of static files to be served from a microcontroller web server.

### Usage
```shell
python compress.py <--compress|--carray> <directory>
```
The `--compress` modifier will compress the files found in the given directory.
The `--carray` modifier will generate a C header file for Arduino. It will contain arrays with gzipped data from the files in `directory`. It will also generate a structure with convenient information:
```C
struct GzipData {
	// path is the file name (relative to given directory)
	// ./static
	//    index.html
	//    assets
	//      favicon.ico
	// will result in:
	// /index.html
	// /assets/favicon.ico
	const char *path;
	const byte *data;
	const size_t dataSize;
};

const struct GzipData gzipDataMap[];
```
### Notes
The directory is searched recursively.
Files with .gz extension will be included, but the script won't try to compress them.

### Dependencies
Python 3.8 and above
