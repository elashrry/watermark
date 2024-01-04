A script to add a given string as a watermark to PDF files.  

If no PDF files are provided, it will run over all existing PDF files.

Running `./watermark.py -h` gives:
```
positional arguments:
  watermark_text        Text for the watermark.

optional arguments:
  -h, --help            show this help message and exit
  -f [file_name ...], --input_files [file_name ...]
                        Path to the input PDF files.
  -x [file_name ...], --exclude [file_name ...]
                        File names to exclude.
```