# Allow direct execution
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import copy
import numpy as np
from unittest import TestCase
from PyQt4.QtCore import *
from lib.sheet import Sheet

#
# test
#

class SheetTestCase(TestCase):

    def setUp(self):
        pass

    def test_init(self):
        sh = Sheet(valueClass=QString)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)

    def test_dimensions(self):
        sh = Sheet(QString, [['1','2']])
        self.assertEqual(sh.rowCount(), 1)
        self.assertEqual(sh.columnCount(), 2)
        #
        sh = Sheet(QString, [['1','2'], ['3','4']])
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 2)
        #
        sh = Sheet(QString, [['1','2'], ['3','4','5']])
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)

    def test_setvalue_str_class(self):
        sh = Sheet(valueClass=str)
        sh.setValue(3, 3, 'cell 3-3')
        self.assertEqual(sh.value(2,2), '')
        self.assertEqual(sh.value(3,3), 'cell 3-3')
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 4)
        #
        sh.setValue(3, 3, 'cell 3-3 new')
        self.assertEqual(sh.value(3,3), 'cell 3-3 new')
        #
        sh.setValue(3, 3, '')
        self.assertEqual(sh.value(3,3), '')
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)

    def test_setvalue(self):
        sh = Sheet(valueClass=QString)
        sh.setValue(3, 3, QString('cell 3-3'))
        self.assertEqual(sh.value(2,2), '')
        self.assertEqual(sh.value(3,3), 'cell 3-3')
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 4)
        #
        sh.setValue(3, 3, QString('cell 3-3 new'))
        self.assertEqual(sh.value(3,3), 'cell 3-3 new')
        #
        with self.assertRaises(IndexError):
            sh.setValue(-1, 2, QString('cell 3-3'))
        with self.assertRaises(IndexError):
            sh.setValue(1, -2, QString('cell 3-3'))
        with self.assertRaises(IndexError):
            sh.setValue(-1, -2, QString('cell 3-3'))
        #
        sh.setValue(3, 3, QString(''))
        self.assertEqual(sh.value(3,3), '')
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)

    def test_typeerror(self):
        sh = Sheet(valueClass=QString)
        with self.assertRaises(TypeError):
            sh.setValue(3, 3, 1000)

    def test_emptySetArrayData(self):
        arrayData = []
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        #
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        self.assertEqual(sh.value(300,300), '')

    def test_setArrayData(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['', QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        #
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-1')
        self.assertEqual(sh.value(2,2), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '3-1')
        self.assertEqual(sh.value(3,2), '')
        self.assertEqual(sh.value(300,300), '')

    def test_remove_column(self):
        sh = Sheet(valueClass=QString)
        #
        # test 1
        #
        sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
        sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeColumn(0)
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 2)
        #
        sh.removeColumn(0)
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 1)
        #
        sh.removeColumn(0)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 2
        #
        sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
        sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeColumn(2)
        self.assertEqual(sh.rowCount(), 1)
        self.assertEqual(sh.columnCount(), 2)
        #
        sh.removeColumn(2)
        #
        sh.removeColumn(1)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        sh.removeColumn(0)

    def test_remove_columns(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['',             QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeColumns(1, 1)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 2)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '')
        #
        # test 2: negative indexes is not allowed
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        with self.assertRaises(IndexError):
            sh.removeColumns(-2, -1)
        #
        # test 3: empty all
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeColumns(0, 3)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(3,0), '')
        self.assertEqual(sh.value(3,1), '')

    def test_remove_row(self):
        sh = Sheet(valueClass=QString)
        #
        # test 1
        #
        sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
        sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeRow(0)
        self.assertEqual(sh.rowCount(), 1)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeRow(0)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 2
        #
        sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
        sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeRow(1)
        self.assertEqual(sh.rowCount(), 1)
        self.assertEqual(sh.columnCount(), 2)
        #
        sh.removeRow(1)
        #
        sh.removeRow(0)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 3
        #
        sh.setValue(row=0, column=1, cellValue=QString('cell 0-1'))
        sh.setValue(row=1, column=2, cellValue=QString('cell 1-1'))
        self.assertEqual(sh.rowCount(), 2)
        self.assertEqual(sh.columnCount(), 3)
        #
        with self.assertRaises(IndexError):
            sh.removeRow(-1)

    def test_remove_rows(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['', QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeRows(1, 1)
        self.assertEqual(sh.rowCount(), 3)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(0,2), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '2-1')
        self.assertEqual(sh.value(1,2), '2-2')
        self.assertEqual(sh.value(2,0), '3-0')
        self.assertEqual(sh.value(2,1), '3-1')
        self.assertEqual(sh.value(2,2), '')
        #
        # test 2
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        with self.assertRaises(IndexError):
            sh.removeRows(-2, -1)
        #
        # test 3
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.removeRows(0, 4)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')

    def test_insert_columns(self):
        arrayData = [['1','2'],
                     ['a','e'],
                     ['6','7'],
                     ['11','12']]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertColumns(0, [['a'],
                             ['b'],
                             ['c'],
                             ['d']])
        self.assertEqual(sh.arrayData(), [['a','1','2'],
                                          ['b','a','e'],
                                          ['c','6','7'],
                                          ['d','11','12']])
        #
        # test 2
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertColumns(2, [['a','a'],
                             ['b','b'],
                             ['c','c'],
                             ['d','d']])
        self.assertEqual(sh.arrayData(), [['1','2','a','a'],
                                          ['a','e','b','b'],
                                          ['6','7','c','c'],
                                          ['11','12','d','d']])
        #
        # test 3
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertColumns(4, [['a'],
                             ['b'],
                             ['c'],
                             ['d']])
        self.assertEqual(sh.arrayData(), [['1','2',None, None,'a'],
                                          ['a','e',None, None,'b'],
                                          ['6','7',None, None,'c'],
                                          ['11','12',None, None,'d']])
        #
        # test 5
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertColumns(0, [['a'],
                             ['b'],
                             ['c']])
        self.assertEqual(sh.arrayData(), [['a','1','2'],
                                          ['b','a','e'],
                                          ['c','6','7'],
                                          [None,'11','12']])
        #
        # test 6
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertColumns(0, [['a ', 'a', 'a'],
                             [None, 'b', 'b'],
                             [None, None,'c'],
                             [None, None,'d'],
                             [None, None,'e']])
        self.assertEqual(sh.arrayData(),[['a ', 'a', 'a', '1', '2'],
                                         [None, 'b', 'b', 'a', 'e'],
                                         [None, None, 'c', '6', '7'],
                                         [None, None, 'd', '11', '12'],
                                         [None, None, 'e', None, None]])

    def test_insert_rows(self):
        arrayData = [['1','2'],
                     ['a','e'],
                     ['6','7'],
                     ['11','12']]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(0, arrayData[0:1])
        self.assertEqual(sh.arrayData(), [['1','2'],
                                          ['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12']])
        #
        # test 2
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(4, arrayData[0:1])
        self.assertEqual(sh.arrayData(), [['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12'],
                                          ['1','2']])
        #
        # test 3
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(0, arrayData[0:2])
        self.assertEqual(sh.arrayData(), [['1','2'],
                                          ['a','e'],
                                          ['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12']])
        #
        # test 4
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(4, arrayData[0:2])
        self.assertEqual(sh.arrayData(), [['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12'],
                                          ['1','2'],
                                          ['a','e']])
        #
        # test 5
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(6, arrayData[0:2])
        self.assertEqual(sh.arrayData(), [['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12'],
                                          [None, None],
                                          [None, None],
                                          ['1','2'],
                                          ['a','e']])
        #
        # test 6
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(0, [['1']])
        self.assertEqual(sh.arrayData(), [['1',None],
                                          ['1','2'],
                                          ['a','e'],
                                          ['6','7'],
                                          ['11','12']])
        #
        # test 7
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertRows(0, [['1'],
                          ['2','3'],
                          ['4'],
                          ['5','6','7']])
        self.assertEqual(sh.arrayData(), [['1',None, None],
                                          ['2','3',None],
                                          ['4',None,None],
                                          ['5','6','7'],
                                          ['1','2',None],
                                          ['a','e',None],
                                          ['6','7',None],
                                          ['11','12',None]])

    def test_insert_empty_row(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['',             QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRow(2)
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(2,3), '')
        self.assertEqual(sh.value(3,0), '')
        self.assertEqual(sh.value(3,1), '2-1')
        self.assertEqual(sh.value(3,2), '2-2')
        self.assertEqual(sh.value(4,0), '3-0')
        self.assertEqual(sh.value(4,1), '3-1')
        #
        # test 2: insert row in tenth position it has no effect
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRow(10)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-1')
        self.assertEqual(sh.value(2,2), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '3-1')
        #
        # test 3
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRow(0)
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '')
        self.assertEqual(sh.value(2,0), '1-0')
        self.assertEqual(sh.value(2,1), '1-1')
        self.assertEqual(sh.value(3,0), '')
        self.assertEqual(sh.value(3,1), '2-1')
        self.assertEqual(sh.value(3,2), '2-2')
        self.assertEqual(sh.value(4,0), '3-0')
        self.assertEqual(sh.value(4,1), '3-1')
        #
        # test 4
        #
        sh = Sheet(valueClass=QString)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        sh.insertEmptyRow(2)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)

    def test_insert_empty_rows(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['',             QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1: insert three rows to the middle
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRows(2, 3)
        self.assertEqual(sh.rowCount(), 7)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(2,3), '')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(2,3), '')
        self.assertEqual(sh.value(4,0), '')
        self.assertEqual(sh.value(4,1), '')
        self.assertEqual(sh.value(4,3), '')
        self.assertEqual(sh.value(5,0), '')
        self.assertEqual(sh.value(5,1), '2-1')
        self.assertEqual(sh.value(5,2), '2-2')
        self.assertEqual(sh.value(6,0), '3-0')
        self.assertEqual(sh.value(6,1), '3-1')
        #
        # test 2: insert three rows to row tenth position it has no effect
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRows(10, 3)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-1')
        self.assertEqual(sh.value(2,2), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '3-1')
        #
        # test 3: insert three rows to the top
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        sh.insertEmptyRows(0, 3)
        self.assertEqual(sh.rowCount(), 7)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(3,0), '')
        self.assertEqual(sh.value(3,1), '')
        self.assertEqual(sh.value(4,0), '1-0')
        self.assertEqual(sh.value(4,1), '1-1')
        self.assertEqual(sh.value(5,0), '')
        self.assertEqual(sh.value(5,1), '2-1')
        self.assertEqual(sh.value(5,2), '2-2')
        self.assertEqual(sh.value(6,0), '3-0')
        self.assertEqual(sh.value(6,1), '3-1')
        #
        # test 4: insert rows in empty sheet results a empty sheet
        #
        sh = Sheet(valueClass=QString)
        sh.insertEmptyRows(2, 10)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 5
        #
        sh = Sheet(valueClass=QString)
        sh.insertEmptyRows(2, 0)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 6: count must be greater or equal than zero
        #
        sh = Sheet(valueClass=QString)
        with self.assertRaises(IndexError):
            sh.insertEmptyRows(2, -1)

    def test_insert_empty_column(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['',             QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1: insert one column to the middle
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumn(2)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 4)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-1')
        self.assertEqual(sh.value(2,2), '')
        self.assertEqual(sh.value(2,3), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '3-1')
        #
        # test 2: insert column in tenth position it has not effect.
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumn(10)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(1,0), '1-0')
        self.assertEqual(sh.value(1,1), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '2-1')
        self.assertEqual(sh.value(2,2), '2-2')
        self.assertEqual(sh.value(3,0), '3-0')
        self.assertEqual(sh.value(3,1), '3-1')
        #
        # test 3
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumn(0)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 4)
        self.assertEqual(sh.value(0,0), '')
        self.assertEqual(sh.value(0,1), '')
        self.assertEqual(sh.value(0,2), '')
        self.assertEqual(sh.value(1,0), '')
        self.assertEqual(sh.value(1,1), '1-0')
        self.assertEqual(sh.value(1,2), '1-1')
        self.assertEqual(sh.value(2,0), '')
        self.assertEqual(sh.value(2,1), '')
        self.assertEqual(sh.value(2,2), '2-1')
        self.assertEqual(sh.value(2,3), '2-2')
        self.assertEqual(sh.value(3,0), '')
        self.assertEqual(sh.value(3,1), '3-0')
        self.assertEqual(sh.value(3,2), '3-1')
        #
        # test 4
        #
        sh = Sheet(valueClass=QString)
        sh.insertEmptyColumn(2)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 5
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy([['1','2']]))
        sh.insertEmptyColumn(1)
        self.assertEqual(sh.arrayData(), [['1',None,'2']])

    def test_insert_empty_columns(self):
        arrayData = [[],
                     [QString('1-0'), QString('1-1')],
                     ['',             QString('2-1'), QString('2-2')],
                     [QString('3-0'), QString('3-1')]]
        #
        # test 1
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumns(2, 3)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 6)
        #
        # test 2: insert three columns to column tenth position it has no effect
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumns(10, 3)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 3)
        #
        # test 3: insert three columns to the top
        #
        sh = Sheet(valueClass=QString, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyColumns(0, 3)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 6)
        #
        # test 4: insert columns in empty sheet results a empty sheet
        #
        sh = Sheet(valueClass=QString)
        sh.insertEmptyColumns(2, 10)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 5
        #
        sh = Sheet(valueClass=QString)
        sh.insertEmptyColumns(2, 0)
        self.assertEqual(sh.rowCount(), 0)
        self.assertEqual(sh.columnCount(), 0)
        #
        # test 6: countColumn must be greater or equal than zero
        #
        sh = Sheet(valueClass=QString)
        with self.assertRaises(IndexError):
            sh.insertEmptyColumns(2, -1)

    def test_move_row(self):
        arrayData = [['1','2','3','4','5'],
                     ['a','e','i','o','u'],
                     ['6','7','8','9','10'],
                     ['11','12','13','14','15']]
        #
        # test 1
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRow(0, 2)
        self.assertEqual(sh.arrayData(),[['a', 'e', 'i', 'o', 'u'],
                                         ['6', '7', '8', '9', '10'],
                                         ['1', '2', '3', '4', '5'],
                                         ['11', '12', '13', '14', '15']])
        #
        # test 2
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRow(2, 5)
        self.assertEqual(sh.arrayData(),[['1', '2', '3', '4', '5'],
                                         ['a', 'e', 'i', 'o', 'u'],
                                         ['11', '12', '13', '14', '15'],
                                         [None, None, None, None, None],
                                         [None, None, None, None, None],
                                         ['6', '7', '8', '9', '10']])

    def test_move_rows(self):
        arrayData = [['1','2','3','4','5'],
                     ['a','e','i','o','u'],
                     ['6','7','8','9','10'],
                     ['11','12','13','14','15']]
        #
        # test 1
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(0, 1, 2)
        self.assertEqual(sh.arrayData(),[['a', 'e', 'i', 'o', 'u'],
                                         ['6', '7', '8', '9', '10'],
                                         ['1', '2', '3', '4', '5'],
                                         ['11', '12', '13', '14', '15']]
)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 2
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(0, 2, 3)
        self.assertEqual(sh.arrayData(),[['6', '7', '8', '9', '10'],
                                         ['11', '12', '13', '14', '15'],
                                         [None, None, None, None, None],
                                         ['1', '2', '3', '4', '5'],
                                         ['a', 'e', 'i', 'o', 'u']]
)
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 3
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(0, 2, 2)
        self.assertEqual(sh.arrayData(), [['6', '7', '8', '9', '10'],
                                          ['11', '12', '13', '14', '15'],
                                          ['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u']]
)
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 4
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(3, 1, 0)
        self.assertEqual(sh.arrayData(), [['11','12','13','14','15'],
                                          ['1','2','3','4','5'],
                                          ['a','e','i','o','u'],
                                          ['6','7','8','9','10']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 5
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(3, 1, 6)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          [None, None, None, None, None],
                                          [None, None, None, None, None],
                                          [None, None, None, None, None],
                                          ['11', '12', '13', '14', '15']])
        self.assertEqual(sh.rowCount(), 7)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 6
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(5, 2, 1)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          [None,None,None,None,None],
                                          [None,None,None,None,None],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 6)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 7
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(3, 2, 1)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['11','12','13','14','15'],
                                          [None,None,None,None,None],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10']])
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 8
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(5, 1, 1)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          [None,None,None,None,None],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 9
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(5, 2, 0)
        self.assertEqual(sh.arrayData(), [[None,None,None,None,None],
                                          [None,None,None,None,None],
                                          ['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 6)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 10
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(5, 2, 4)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 11
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(50, 20, 40)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 12
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(0, 1, 5)
        self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11', '12', '13', '14', '15'],
                                          [None, None, None, None, None],
                                          [None, None, None, None, None],
                                          ['1', '2', '3', '4', '5']])
        self.assertEqual(sh.rowCount(), 6)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 13
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(0, 1, 7)
        self.assertEqual(sh.arrayData(), [['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          ['11','12','13','14','15'],
                                          [None,None,None,None,None],
                                          [None,None,None,None,None],
                                          [None,None,None,None,None],
                                          [None,None,None,None,None],
                                          ['1', '2', '3', '4', '5']])
        self.assertEqual(sh.rowCount(), 8)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 14
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(7, 1, 3)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          [None, None, None, None, None],
                                          ['11', '12', '13', '14', '15']])
        self.assertEqual(sh.rowCount(), 5)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 15
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveRows(7, 2, 3)
        self.assertEqual(sh.arrayData(), [['1', '2', '3', '4', '5'],
                                          ['a', 'e', 'i', 'o', 'u'],
                                          ['6', '7', '8', '9', '10'],
                                          [None, None, None, None, None],
                                          [None, None, None, None, None],
                                          ['11', '12', '13', '14', '15']])
        self.assertEqual(sh.rowCount(), 6)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 16
        #
        sh = Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        with self.assertRaises(IndexError):
            sh.moveRows(-1, 2, 2)
        with self.assertRaises(IndexError):
            sh.moveRows(2, 0, 3)

    def test_move_columns(self):
        arrayData = [['1','2','3','4','5'],
                     ['a','e','i','o','u'],
                     ['6','7','8','9','10'],
                     ['11','12','13','14','15']]
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(0, 1, 2)
        self.assertEqual(sh.arrayData(),[['2', '3', '1', '4', '5'],
                                         ['e', 'i', 'a', 'o', 'u'],
                                         ['7', '8', '6', '9', '10'],
                                         ['12', '13', '11', '14', '15']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(0, 2, 3)
        self.assertEqual(sh.arrayData(),[['3', '4', '5', '1', '2'],
                                         ['i', 'o', 'u', 'a', 'e'],
                                         ['8', '9', '10', '6', '7'],
                                         ['13', '14', '15', '11', '12']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(0, 1, 6)
        self.assertEqual(sh.arrayData(),[['2', '3', '4', '5', None, None, '1'],
                                         ['e', 'i', 'o', 'u', None, None, 'a'],
                                         ['7', '8', '9', '10', None, None, '6'],
                                         ['12', '13', '14', '15', None, None, '11']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 7)
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(50, 2, 100)
        self.assertEqual(sh.arrayData(), [['1','2','3','4','5'],
                                          ['a','e','i','o','u'],
                                          ['6','7','8','9','10'],
                                          ['11','12','13','14','15']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 5
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(4, 1, 2)
        self.assertEqual(sh.arrayData(), [['1','2','5','3','4'],
                                          ['a','e','u','i','o'],
                                          ['6','7','10','8','9'],
                                          ['11','12','15','13','14']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 5)
        #
        # test 6
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(4, 3, 2)
        self.assertEqual(sh.arrayData(), [['1','2','5',None,None,'3','4'],
                                          ['a','e','u',None,None,'i','o'],
                                          ['6','7','10',None,None,'8','9'],
                                          ['11','12','15',None,None,'13','14']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 7)
        #
        # test 6
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveColumns(10, 3, 2)
        self.assertEqual(sh.arrayData(), [['1','2',None,None,None,'3','4','5'],
                                          ['a','e',None,None,None,'i','o','u'],
                                          ['6','7',None,None,None,'8','9','10'],
                                          ['11','12',None,None,None,'13','14','15']])
        self.assertEqual(sh.rowCount(), 4)
        self.assertEqual(sh.columnCount(), 8)

    def test_empty_cells_in_rows(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyCellsInRows(1, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', None  , None  , '2000', '2100', '2200'],
                                         ['2300', None  , None  , '2600', '2700', '2800'],
                                         ['2900', '1800', '1900', '3200', '3300', '3400'],
                                         [None  , '2400', '2500', None  , None  , None],
                                         [None  , '3000', '3100', None  , None  , None]])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyCellsInRows(2, 2, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', None , None   , '2700', '2800'],
                                         ['2900', '3000', None , None   , '3300', '3400'],
                                         [None  , None  , '2500', '2600', None  , None],
                                         [None  , None  , '3100', '3200', None  , None]])
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertEmptyCellsInRows(3, 3, 1, 3)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', None,    None,   None],
                                         [None,   None,   None,   '3200', '3300', '3400']])
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        with self.assertRaises(IndexError):
            sh.insertEmptyCellsInRows(3, 3, 0, 0)
        #
        # test 5
        #
        sh=Sheet(valueClass=str)
        with self.assertRaises(IndexError):
            sh.insertEmptyCellsInRows(3, 3, 0, 0)

    def test_array_in_rows(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sourceData = np.empty([2,2], dtype=object).tolist()
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(1, 1, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', None  , None  , '2000', '2100', '2200'],
                                         ['2300', None  , None  , '2600', '2700', '2800'],
                                         ['2900', '1800', '1900', '3200', '3300', '3400'],
                                         [None  , '2400', '2500', None  , None  , None],
                                         [None  , '3000', '3100', None  , None  , None]])
        #
        # test 2
        #
        sourceData = np.empty([2,2], dtype=object).tolist()
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(2, 2, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', None , None   , '2700', '2800'],
                                         ['2900', '3000', None , None   , '3300', '3400'],
                                         [None  , None  , '2500', '2600', None  , None],
                                         [None  , None  , '3100', '3200', None  , None]])
        #
        # test 3
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(3, 3, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', 'a',    'b',    'c'],
                                         [None,   None,   None,   '3200', '3300', '3400']])
        #
        # test 4
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(3, 4, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None],
                                         ['2900', '3000', '3100', '3200', 'a',    'b',    'c'],
                                         [None,   None,   None,   None,   '3300', '3400', None]])
        #
        # test 5
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(3, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', 'a',  'b',  'c']])
        #
        # test 6
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(4, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None,   None,   None,   None,   None,   None,   'a',  'b',  'c']])
        #
        # test 7
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None,   None,   None,   None,   None,   None,   None, None, None],
                                         [None,   None,   None,   None,   None,   None,   'a',  'b',  'c']])
        #
        # test 8
        #
        sourceData = [['a','b','c'],['d','e','f']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None,   None,   None,   None,   None,   None,   None, None, None],
                                         [None,   None,   None,   None,   None,   None,   'a',  'b',  'c'],
                                         [None,   None,   None,   None,   None,   None,   'd',  'e',  'f']])
        #
        # test 9
        #
        sourceData = [[]]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']]);
        #
        # test 10
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(0, 0, sourceData)
        self.assertEqual(sh.arrayData(),[['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']]);
        #
        # test 11
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInRows(0, 0, sourceData)
        self.assertEqual(sh.arrayData(),[['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         ['1100', '1200', '1300', '1400', '1500', '1600', None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None]]);
        #
        # test 12
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=[])
        sh.insertArrayInRows(5, 2, sourceData)
        self.assertEqual(sh.arrayData(),[[None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]);

    def test_delete_cells(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(1, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700',None  ,None  ,'2000','2100','2200'],
                                         ['2300',None  ,None  ,'2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(0, 0, 1, 1)
        self.assertEqual(sh.arrayData(),[[None, '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(3, 0, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100', '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         [None,'3000','3100','3200','3300','3400']])
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(3, 0, 1, 6)
        self.assertEqual(sh.arrayData(),[['1100', '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800']])
        #
        # test 5
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(3, 0, 2, 7)
        self.assertEqual(sh.arrayData(),[['1100', '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800']])
        #
        # test 6
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(2, 1, 2, 5)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', None, None, None, None, None],
                                         ['2900', None, None, None, None, None]])
        #
        # test 7
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(2, 1, 20, 70)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', None, None, None, None, None],
                                         ['2900', None, None, None, None, None]])
        #
        # test 8
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(0, 6, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100', '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 9
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.deleteCells(4, 0, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100', '1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 10
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        with self.assertRaises(IndexError):
            sh.deleteCells(0, 0, 0, 0)
        with self.assertRaises(IndexError):
            sh.deleteCells(1, 1, 0, 0)
        with self.assertRaises(IndexError):
            sh.deleteCells(0, 0, -1, -1)

    def test_array_in_columns(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sourceData = np.empty([2,2], dtype=object).tolist()
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(1, 1, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None],
                                         ['1700', None, None, '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', None, None, '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None]])
        #
        # test 2
        #
        sourceData = np.empty([2,2], dtype=object).tolist()
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(2, 4, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None],
                                         ['2300', '2400', '2500', '2600', None, None, '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', None, None, '3300', '3400']])
        #
        # test 3
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(3, 4, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', 'a', 'b', 'c', '3300', '3400']])
        #
        # test 4
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(3, 5, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', 'a',    'b',   'c', '3400']])
        #
        # test 5
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(3, 6, sourceData)
        self.assertEqual(sh.arrayData(), [['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                          ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                          ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                          ['2900', '3000', '3100', '3200', '3300', '3400', 'a', 'b', 'c']])
        #
        # test 6
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(4, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None, None, None, None, None, None, 'a', 'b', 'c']])
        #
        # test 7
        #
        sourceData = [['a','b','c']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, 'a', 'b', 'c']])
        #
        # test 8
        #
        sourceData = [['a','b','c'],['d','e','f']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600', None, None, None],
                                         ['1700', '1800', '1900', '2000', '2100', '2200', None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400', None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, 'a', 'b', 'c'],
                                         [None, None, None, None, None, None, 'd', 'e', 'f']])
        #
        # test 9
        #
        sourceData = [[]]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(5, 6, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']]);
        #
        # test 10
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(0, 0, sourceData)
        self.assertEqual(sh.arrayData(),[['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '2900', '3000', '3100', '3200', '3300', '3400']]);
        #
        # test 11
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.insertArrayInColumns(0, 1, sourceData)
        self.assertEqual(sh.arrayData(),[['1100', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', '3000', '3100', '3200', '3300', '3400']]);
        #
        # test 12
        #
        sourceData = [['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                      ['xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']]
        sh=Sheet(valueClass=str, arrayData=[])
        sh.insertArrayInColumns(5, 2, sourceData)
        self.assertEqual(sh.arrayData(),[[None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, None, None, None, None, None, None, None],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx'],
                                         [None, None, 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx', 'xxxx']])

    def test_remove_array_in_columns(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 0
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 0, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1900','2000','2100','2200'   , None ,   None],
                                         ['2500','2600','2700','2800'   , None ,   None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '2000', '2100', '2200', None,   None],
                                         ['2300', '2600', '2700', '2800', None,   None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 2, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '2100', '2200', None,    None],
                                         ['2300', '2400', '2700', '2800', None,    None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])


        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 3, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2200', None  , None],
                                         ['2300', '2400', '2500', '2800', None  , None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 4, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', None, None],
                                         ['2300', '2400', '2500', '2600', None, None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 5
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 5, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', None],
                                         ['2300', '2400', '2500', '2600', '2700', None],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 6
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 6, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 7
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 7, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 8
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 0, 2, 6)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         [None  ,None  ,None  ,None  ,None  ,None],
                                         [None  ,None  ,None  ,None  ,None  ,None],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 9
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 0, 3, 6)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600']])
        #
        # test 10
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 0, 4, 6)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600']])
        #
        # test 11
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(0, 0, 4, 6)
        self.assertEqual(sh.arrayData(),[])
        #
        # test 12
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(0, 0, 10, 10)
        self.assertEqual(sh.arrayData(),[])
        #
        # test 13
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        with self.assertRaises(IndexError):
            sh.removeArrayInColumns(0, 0, 0, 0)
        with self.assertRaises(IndexError):
            sh.removeArrayInColumns(1, 1, 0, 0)
        with self.assertRaises(IndexError):
            sh.removeArrayInColumns(0, 0, -1, -1)
        #
        # test 14
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(1, 1, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1900','2000','2100','2200', None],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 15
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(3, 5, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300',None]])
        #
        # test 16
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(3, 5, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300',None]])
        #
        # test 17
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInColumns(0, 0, 4, 1)
        self.assertEqual(sh.arrayData(),[['1200','1300','1400','1500','1600'],
                                         ['1800','1900','2000','2100','2200'],
                                         ['2400','2500','2600','2700','2800'],
                                         ['3000','3100','3200','3300','3400']])

    def test_remove_array_in_rows(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 0
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '2400', '2500', '1400', '1500', '1600'],
                                         ['1700', '3000', '3100', '2000', '2100', '2200'],
                                         ['2300', None, None, '2600', '2700', '2800'],
                                         ['2900', None, None, '3200', '3300', '3400']])
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(1, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '3000', '3100', '2000', '2100', '2200'],
                                         ['2300', None, None, '2600', '2700', '2800'],
                                         ['2900', None, None, '3200', '3300', '3400']])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(2, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', None, None, '2600', '2700', '2800'],
                                         ['2900', None, None, '3200', '3300', '3400']])
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(3, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', None, None, '3200', '3300', '3400']])
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(4, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 5
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(5, 1, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 8
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 1, 2, 6)
        self.assertEqual(sh.arrayData(),[['1100', '2400', '2500', '2600', '2700', '2800'],
                                         ['1700', '3000', '3100', '3200', '3300', '3400'],
                                         ['2300', None, None, None, None, None],
                                         ['2900', None, None, None, None, None]])
        #
        # test 9
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 1, 3, 6)
        self.assertEqual(sh.arrayData(),[['1100', '3000', '3100', '3200', '3300', '3400'],
                                         ['1700', None, None, None, None, None],
                                         ['2300', None, None, None, None, None],
                                         ['2900', None, None, None, None, None]])
        #
        # test 10
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 1, 4, 6)
        self.assertEqual(sh.arrayData(),[['1100'],
                                         ['1700'],
                                         ['2300'],
                                         ['2900']])
        #
        # test 11
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 0, 4, 6)
        self.assertEqual(sh.arrayData(),[])
        #
        # test 12
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 0, 10, 10)
        self.assertEqual(sh.arrayData(),[])
        #
        # test 13
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        with self.assertRaises(IndexError):
            sh.removeArrayInRows(0, 0, 0, 0)
        with self.assertRaises(IndexError):
            sh.removeArrayInRows(1, 1, 0, 0)
        with self.assertRaises(IndexError):
            sh.removeArrayInRows(0, 0, -1, -1)
        #
        # test 14
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(1, 1, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '2400', '1900', '2000', '2100', '2200'],
                                         ['2300', '3000', '2500', '2600', '2700', '2800'],
                                         ['2900', None, '3100', '3200', '3300', '3400']])
        #
        # test 15
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(3, 5, 1, 1)
        self.assertEqual(sh.arrayData(),[['1100', '1200', '1300', '1400', '1500', '1600'],
                                         ['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', None]])
        #
        # test 16
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(3, 5, 2, 2)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300',None]])
        #
        # test 17
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.removeArrayInRows(0, 0, 1, 6)
        self.assertEqual(sh.arrayData(),[['1700', '1800', '1900', '2000', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])

    def test_get_array(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        #
        # test 1
        #
        array = sh.getArray(1, 0, 2, 2).tolist()
        self.assertEqual(array,[['1700', '1800'],
                                ['2300', '2400']])
        #
        # test 2
        #
        array = sh.getArray(3, 0, 2, 2).tolist()
        self.assertEqual(array, [['2900', '3000'],
                                 [None, None]])
        #
        # test 3
        #
        with self.assertRaises(IndexError):
            sh.getArray(0, 0, 0, 0)
        with self.assertRaises(IndexError):
            sh.getArray(1, 1, 0, 0)
        with self.assertRaises(IndexError):
            sh.getArray(0, 0, -1, -1)
        #
        # test 4
        #
        array = sh.getArray(3, 5, 1, 1).tolist()
        self.assertEqual(array, [['3400']])
        #
        # test 5
        #
        array = sh.getArray(3, 5, 2, 2).tolist()
        self.assertEqual(array, [['3400', None],
                                 [None, None]])
        #
        # test 6
        #
        array = sh.getArray(3, 6, 2, 2).tolist()
        self.assertEqual(array, [[None, None],
                                 [None, None]])

    def test_move_array_in_rows(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInRows(0, 0, 2, 2, 2, 0)
        self.assertEqual(sh.arrayData(),[['2300', '2400', '1300', '1400', '1500', '1600'],
                                         ['2900', '3000', '1900', '2000', '2100', '2200'],
                                         ['1100', '1200', '2500', '2600', '2700', '2800'],
                                         ['1700', '1800', '3100', '3200', '3300', '3400']])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInRows(1, 0, 2, 2, 1, 0)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInRows(0, 0, 2, 2, 3, 0)
        self.assertEqual(sh.arrayData(),[['2300', '2400', '1300', '1400', '1500', '1600'],
                                         ['2900', '3000', '1900', '2000', '2100', '2200'],
                                         [None,    None,  '2500', '2600', '2700', '2800'],
                                         ['1100', '1200', '3100', '3200', '3300', '3400'],
                                         ['1700', '1800',  None,   None,   None,   None]]
)
    def test_move_array_in_columns(self):
        arrayData = [['1100','1200','1300','1400','1500','1600'],
                     ['1700','1800','1900','2000','2100','2200'],
                     ['2300','2400','2500','2600','2700','2800'],
                     ['2900','3000','3100','3200','3300','3400']]
        #
        # test 1
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInColumns(0, 0, 2, 2, 2, 0)
        self.assertEqual(sh.arrayData(),[['1300', '1400', '1500', '1600', None, None, None, None],
                                         ['1900', '2000', '2100', '2200', None, None, None, None],
                                         ['1100', '1200', '2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['1700', '1800', '2900', '3000', '3100', '3200', '3300', '3400']])
        #
        # test 2
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInColumns(1, 0, 2, 2, 1, 0)
        self.assertEqual(sh.arrayData(),[['1100','1200','1300','1400','1500','1600'],
                                         ['1700','1800','1900','2000','2100','2200'],
                                         ['2300','2400','2500','2600','2700','2800'],
                                         ['2900','3000','3100','3200','3300','3400']])
        #
        # test 3
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInColumns(0, 0, 2, 2, 3, 0)
        self.assertEqual(sh.arrayData(),[['1300', '1400', '1500', '1600', None, None, None, None],
                                         ['1900', '2000', '2100', '2200', None, None, None, None],
                                         ['2300', '2400', '2500', '2600', '2700', '2800', None, None],
                                         ['1100', '1200', '2900', '3000', '3100', '3200', '3300', '3400'],
                                         ['1700', '1800', None, None, None, None, None, None]])
        #
        # test 4
        #
        sh=Sheet(valueClass=str, arrayData=copy.deepcopy(arrayData))
        sh.moveArrayInColumns(0, 0, 2, 2, 0, 2)
        self.assertEqual(sh.arrayData(),[['1300', '1400', '1100', '1200', '1500', '1600'],
                                         ['1900', '2000', '1700', '1800', '2100', '2200'],
                                         ['2300', '2400', '2500', '2600', '2700', '2800'],
                                         ['2900', '3000', '3100', '3200', '3300', '3400']])

if __name__ == '__main__':
    unittest.main()


