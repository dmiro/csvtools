from PyQt4.QtCore import *
from PyQt4.QtGui import *
import json

class ClipboardFormat(object):

    @staticmethod
    def toClipboard(rectangularArea):
        """from rectangular area (two dimension matrix) to clipboard format"""
        if rectangularArea:
            textClip = ''
            for row in rectangularArea:
                textClip = textClip + '\t'.join(row) + '\n'
            return textClip
        return None

    @staticmethod
    def toJSON(rectangularArea):
        """from rectangular area (two dimension matrix) to JSON clipboard format"""
        if rectangularArea:
            textClip = json.dumps(rectangularArea)
            return textClip
        return None

    @staticmethod
    def toDelimitied(rectangularArea):
        """from rectangular area (two dimension matrix) to delimitied clipboard format"""
        if rectangularArea:
            textClip = ''
            for row in rectangularArea:
                textClip = textClip + ','.join(row) + '\n'
            return textClip
        return None

    @staticmethod
    def toXML(rectangularArea):
        """from rectangular area (two dimension matrix) to XML clipboard format"""
        if rectangularArea:
            textClip = ''
            header = rectangularArea[0]
            for row in rectangularArea[1:]:
                items = ['\t\t<{0}>{1}</{2}>\n'.format(header[index], value, header[index]) for index, value in enumerate(row)]
                textClip = textClip + '\t<ROW>\n{0}\t</ROW>\n'.format(''.join(items))
            return '<?xml version="1.0"?>\n<TABLE>\n{0}</TABLE>\n'.format(textClip)
        return None

    @staticmethod
    def toText(rectangularArea):
        """from rectangular area (two dimension matrix) to text clipboard format"""
        if rectangularArea:
            spacerHeaderAdded = False
            textClip = ''
            columnsWidth = [max(len(str(x)) for x in line) for line in zip(*rectangularArea)]
            for row in rectangularArea:
                # format row
                rowFormatted = []
                for index, value in enumerate(row):
                    valueFormatted = '{0:{fill}{align}{width}}'.format(value, fill=' ', align='<', width=columnsWidth[index])
                    rowFormatted.append(valueFormatted)
                textClip = textClip + ' '.join(rowFormatted) + '\n'
                # format row spacer header
                if not spacerHeaderAdded:
                    spacerHeaderAdded = True
                    rowFormatted = []
                    for index in xrange(len(row)):
                        valueFormatted = '{0:{fill}{align}{width}}'.format('', fill='-', align='<', width=columnsWidth[index])
                        rowFormatted.append(valueFormatted)
                    textClip = textClip + ' '.join(rowFormatted) + '\n'

            return textClip
        return None

    @staticmethod
    def toHTML(rectangularArea):
        """from rectangular area (two dimension matrix) to XML clipboard format"""
        if rectangularArea:
            header = rectangularArea[0]
            items = ['<th>{0}</th>'.format(value) for value in header]
            textClip = '\t\t\t<tr>{0}</tr>'.format(''.join(items))
            for row in rectangularArea[1:]:
                items = ['<td>{0}</td>'.format(value) for value in row]
                textClip = textClip + '\n\t\t\t<tr>{0}</tr>'.format(''.join(items))

            return """
<html>
    <head><META content="text/html;"></head>
    <body>

        <style type="text/css">
            table{{
                border-collapse: collapse;
                border: 1px solid black;
            }}
            table td
            {{
                border: 1px solid black;
            }}
        </style>

        <table>
{0}
        </table>

    </body>
</html>""".format(textClip)
        return None

    @staticmethod
    def toPythonText(rectangularArea):
        if rectangularArea:
            text = ClipboardFormat.toText(rectangularArea)
            return 'data = ''"""\n{0}\n"""\n'''.format(text)
        return None

    @staticmethod
    def toPythonTuple(rectangularArea):
        if rectangularArea:
            data = tuple(tuple(row) for row in rectangularArea)
            return 'data = {0}'.format(data.__str__())
        return None

    @staticmethod
    def toPythonList(rectangularArea):
        if rectangularArea:
            return 'data = {0}'.format(rectangularArea.__str__())
        return None

    @staticmethod
    def toPythonDict(rectangularArea):
        if rectangularArea:
            data = {}
            numColumns = len(rectangularArea[0])
            for colIndex in xrange(numColumns):
                column = []
                for row in rectangularArea[1:]:
                    column.append(row[colIndex])
                data[rectangularArea[0][colIndex]] = column
            return 'data = {0}'.format(data.__str__())
        return None

