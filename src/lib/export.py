from PyQt4.QtCore import *
from PyQt4.QtGui import *
import json

def rectangularAreaToClipboardFormat(rectangularArea):
    """from rectangular area (two dimension matrix) to clipboard format"""
    if rectangularArea:
        textClip = ''    
        for row in rectangularArea:
            textClip = textClip + '\t'.join(row) + '\n'
        return textClip
    return None

def rectangularAreaToJSONClipboardFormat(rectangularArea):
    """from rectangular area (two dimension matrix) to JSON clipboard format"""
    if rectangularArea:
        textClip = json.dumps(rectangularArea)   
        return textClip
    return None

def rectangularAreaToDelimitiedClipboardFormat(rectangularArea):
    """from rectangular area (two dimension matrix) to delimitied clipboard format"""
    if rectangularArea:
        textClip = ''    
        for row in rectangularArea:
            textClip = textClip + ','.join(row) + '\n'
        return textClip
    return None

def rectangularAreaToXMLClipboardFormat(rectangularArea):
    """from rectangular area (two dimension matrix) to XML clipboard format"""
    if rectangularArea:
        textClip = ''
        header = rectangularArea[0]
        for row in rectangularArea[1:]:
            items = ['\t\t<{0}>{1}</{2}>\n'.format(header[index], value, header[index]) for index, value in enumerate(row)]
            textClip = textClip + '\t<ROW>\n{0}\t</ROW>\n'.format(''.join(items))    
        return '<?xml version="1.0"?>\n<TABLE>\n{0}</TABLE>\n'.format(textClip)
    return None

def rectangularAreaToTextClipboardFormat(rectangularArea):
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

def rectangularAreaToHTMLClipboardFormat(rectangularArea):
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
            """.format(textClip)
    return None

def rectangularAreaToPythonTextClipboardFormat(rectangularArea):
    if rectangularArea:
        text = rectangularAreaToTextClipboardFormat(rectangularArea)
        return 'data = ''"""\n{0}\n"""\n'''.format(text)
    return None

def rectangularAreaToPythonTupleClipboardFormat(rectangularArea):
    if rectangularArea:
        data = tuple(tuple(row) for row in rectangularArea)
        return 'data = {0}'.format(data.__str__())
    return None

def rectangularAreaToPythonListClipboardFormat(rectangularArea):
    if rectangularArea:
        return 'data = {0}'.format(rectangularArea.__str__())
    return None

def rectangularAreaToPythonDictClipboardFormat(rectangularArea):
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
