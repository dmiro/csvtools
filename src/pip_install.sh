rem 1.
rem download & install PyQt4 32 bit from:  
rem http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt4-4.11.4-gpl-Py2.7-Qt4.8.7-x32.exe

rem 2.
rem install xlrd to load xsl/xslt.
rem https://pypi.python.org/pypi/xlrd
pip install xlrd

rem 3.
rem cChardet is high speed universal character encoding detector. - binding to charsetdetect.
rem Requires Cython: http://www.cython.org/
rem https://github.com/PyYoshi/cChardet
rem pip install -U cchardet

rem 4.
rem The API of the csv module in Python 2 is drastically different from the csv module in Python 3. This is due, for the most part, to the difference between str in Python 2 and Python 3.
rem The semantics of Python 3's version are more useful because they support unicode natively, while Python 2's csv does not.
rem https://github.com/ryanhiebert/backports.csv
rem pip install backports.csv
