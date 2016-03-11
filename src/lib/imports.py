from PyQt4.QtCore import *
from PyQt4.QtGui import *
import json

class ClipboardFormat(object):

    ## http://python.6.x6.nabble.com/Paste-entire-column-into-QTableView-from-Excel-td5016995.html
    @staticmethod
    def toMatrix(textClip):
        """from clipboard format to rectangular area (two dimension matrix)"""
        matrix = []
        rows = textClip.split('\n')
        if rows:
            if not rows[-1].trimmed():
                del(rows[-1])
            for row in rows:
                values = row.split('\t')
                matrix.append(values)
        return matrix

