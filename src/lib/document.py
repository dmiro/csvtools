from abc import *
from json import *
from inspect import *
import csv
import xlrd
from PyQt4.QtCore import *


class QABCMeta(pyqtWrapperType, ABCMeta):   # problem in your case is that the classes you try to inherit from 
    pass                                    # have different metaclasses: 
                                            # http://www.gulon.co.uk/2012/12/28/pyqt4-qobjects-and-metaclasses/

class Document(QObject):
    __metaclass__ = QABCMeta

    loadRequested = pyqtSignal()
    saveRequested = pyqtSignal()

    def __init__(self,
                 filename,
                 **kvparams):               # it's mandatory for serialization/deserialization purposes
        super(Document, self).__init__()
        self.filename = filename
        self.data_ = []
        self.canLoad = True
        self.canSave = False
        self.dataModified = False

    @abstractmethod
    def load(self):
        self.loadRequested.emit()

    @abstractmethod
    def save(self):
        self.saveRequested.emit()

    @property
    def data(self):
        return self.data_

    @data.setter
    def data(self, value):
        self.dataModified = True
        self.data_ = value

    def toJson(self):
        """Convert Document object to json string.
        :return: json string
        """
        class _Encoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Document):
                    d = {'__class__': obj.__class__.__name__,
                         '__module__': obj.__module__}
                    obj.__dict__.pop('data_')  # data_ is not serializable
                    d.update(obj.__dict__)
                    return d
                if not isfunction(obj):                    
                    return super(_Encoder, self).default(obj)
        return _Encoder().encode(self)

    @classmethod
    def fromJson(cls, json_):
        """Convert json string to Document object.
        :param json_: json string
        :return: Document object
        """
        class _Decoder(JSONDecoder):

            def __init__(self):
                JSONDecoder.__init__(self, object_hook=self.dict_to_object)

            @staticmethod
            def dict_to_object(dict_):
                if '__class__' in dict_:
                    class_name = dict_.pop('__class__')
                    module_name = dict_.pop('__module__')
                    module = __import__(module_name)
                    class_ = getattr(module, class_name)
                    obj = class_(**dict_)
                    for k, v in dict_.iteritems():
                        setattr(obj, k, v)
                    return obj
                return dict_
        return _Decoder().decode(json_)


class Csv(Document):

    def __init__(self,
                 filename,
                 delimiter=csv.excel.delimiter,
                 doublequote=csv.excel.doublequote,
                 escapechar=csv.excel.escapechar,
                 lineterminator=csv.excel.lineterminator,
                 quotechar=csv.excel.quotechar,
                 quoting=csv.excel.quoting,
                 skipinitialspace=csv.excel.skipinitialspace,
                 **kvparams):
        super(Csv, self).__init__(filename)
        self.delimiter = delimiter
        self.doublequote= doublequote
        self.escapechar= escapechar
        self.lineterminator= lineterminator
        self.quotechar= quotechar
        self.quoting= quoting
        self.skipinitialspace= skipinitialspace

    def load(self):     
        self.data_ = []
        with open(self.filename, 'rb') as f:
            reader = csv.reader(f,
                                delimiter=self.delimiter,
                                doublequote=self.doublequote,
                                escapechar = self.escapechar,
                                lineterminator= self.lineterminator,
                                quotechar=self.quotechar,
                                quoting=self.quoting,
                                skipinitialspace=self.skipinitialspace)
            for row in reader:
                self.data_.append(row)
        super(Csv, self).load()

    def save(self):
        pass


class Xsl(Document):

    def __init__(self,
                 filename,
                 sheetname,
                 **kvparams):
        super(Xsl, self).__init__(filename)
        self.sheetname = sheetname

    def load(self):
        self.data_ = []
        wb = xlrd.open_workbook(self.filename)
        sh = wb.sheet_by_name(self.sheetname) 
        for rownum in xrange(sh.nrows):
            self.data_.append(sh.row_values(rownum))
        super(Xsl, self).load()

    def save(self):
        pass
        

if __name__ == "__main__":
    d = Csv('..\\..\\testdocs\\demo3.csv', delimiter =';')
    d.load()
    print d.data
    js = d.toJson()
    print js
    d2 = Document.fromJson(json_=js)
    print dir(d2)
    print d2.__class__.__name__
    print d2.filename
    print d2.skipinitialspace
    #print d2.load()
