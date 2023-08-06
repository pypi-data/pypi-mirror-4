NAME
----
__br__ (Batch Rename)

SYNOPIS
-------
br [ __-h __ ] [ __-v__ ] [ __-o__ ] [ __-t__ ] [ __-i INDEXES__ ] [ __-d DIRECTORY__ ] [ __-p PATTERN__ ] ...

DESCRIPTION
-----------
__BR__  (Batch Rename) is an unix utility to ease renaming of a batch of files.

__-o__, __--output__
cause __br__ to be verbose, showing files after they are renamed

__-t__, __--test__
test run, enables __--output__ too

__-i__, __--indexes__=_INDEXES_
substring of indexes that need to be replaced with the new title, in form of x:y

__-d__, __--directory__=_DIRECTORY_
directory containing batch of files

__-p__, __--pattern__=_PATTERN_
regular expression for renaming pattern

_TITLE_ new title to replace the old one

__-h__, __--help__
Display help information and exit.

__-v__, __--version__
Display version information and exit.

FILES
-----
+ `setup.py`  		traditional easy_install or pip
+ `setup.cfg` 		for distutils2 installation
+ `scripts/br`		executable binary
+ `br/__init__.py` 	a separate library packaged version

EXAMPLES
--------
```bash
MrmacHD:~$ ls *.txt
111111.txt 222222.txt 333333.txt
MrmacHD:~$ br -t -i 2:3 -p \*.txt test
111111.txt -> 11test111.txt
222222.txt -> 22test222.txt
333333.txt -> 33test333.txt
``` 

STANDARDS
---------


SEE ALSO
--------

AUTHOR
------
MrmacHD <mrmachd@gmail.com>

BUGS
----

