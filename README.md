# Gzip data to C arrays
Compress files in a tree or generate C byte arrays (gzipped) from them.

## Motivation
This script is intended to use for compression of static files to be served from a microcontroller web server (using Arduino tools).

### Usage
```shell
python compress.py <directory> <-c output-file> <--root>
```
- The `directory` argument is the root of the filesystem you want to compress.
- Use `-c filename` if you want to generate a C header file instead.
- The `--root` modifier will include the name of the root directory in the resulting URL. Use only with `-c`.
- The resulting C file will have the following format:
```C
struct GzipData {
	// path is the resulting URL
	// ./static
	//    index.html
	//    assets
	//      favicon.ico
	// will result in:
	// /index.html or /static/index.html if --root was provided
	// /assets/favicon.ico or /static/assets/favicon.ico if --root was provided
	const char *path;
	const byte *data;
	const size_t dataSize;
};

const struct GzipData gzipDataMap[];
```

Two variables will be created from the definitions above:
```C
#include <Arduino.h>

const byte out_index_html_gz[] PROGMEM = {
	// ...
};

// Definitions above not repeated
// .....
//

// Example
const struct GzipData gzipDataMap[] = {
    { "/dist/index.html", out_index_html_gz, 307 },
    { "/dist/main.bundle.css", out_main_bundle_css_gz, 11258 },
    { "/dist/main.bundle.js", out_main_bundle_js_gz, 59387 }
};

const size_t gzipDataCount = 3;
```

### Notes
The directory is searched recursively.
Files with .gz extension are included unmodified.

### Dependencies
Python 3.8 and above
