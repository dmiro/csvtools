from abc import *
from json import *
from inspect import *
from backports import csv
import xlrd
from PyQt4.QtCore import *
import io
import sys
import cchardet
from lib.commandsheet import CommandSheet
from datetime import datetime
import lib.helper as helper


class NewFilenameFactory(object):
    """class to obtain temporary name for a new file
    """
    newIdFilename = 1
    @classmethod
    def getNewFilename(cls):
        newFilename = 'new {}'.format(cls.newIdFilename)
        cls.newIdFilename = cls.newIdFilename + 1
        return newFilename


class QABCMeta(pyqtWrapperType, ABCMeta):   # inherit from different metaclasses:
    pass                                    # http://www.gulon.co.uk/2012/12/28/pyqt4-qobjects-and-metaclasses/


class Document(CommandSheet):
    __metaclass__ = QABCMeta

    loadRequested = pyqtSignal()
    saveRequested = pyqtSignal()
    fileChanged = pyqtSignal()

    #
    # init
    #

    def __init__(self,
                 filename,
                 **kvparams):               # it's mandatory for serialization/deserialization purposes

        super(Document, self).__init__(valueClass=QString)
        self.filename = filename
        self.encoding_ = ''
        self.canSave = False
        self.isNew = False

    #
    # private
    #

    def __fileChanged(self, filename):
        self.fileChanged.emit()

    #
    # protected
    #

    def _watchFile(self):
        self.__watcher = QFileSystemWatcher()
        self.__watcher.fileChanged.connect(self.__fileChanged)
        self.__watcher.addPath(self.filename)

    def _unwatchFile(self):
        try:
            self.__watcher.fileChanged.disconnect(self.__fileChanged)
            del(self.__watcher)
        except: pass

    #
    # public
    #

    @abstractmethod
    def new(self):
        self.encoding_ = 'UTF-8'
        self.isNew = True

    @abstractmethod
    def load(self, linesToLoad=-1):
        self.isNew = False
        self._watchFile()
        self.loadRequested.emit()

    @abstractmethod
    def save(self, newFilename=None):
        self.isNew = False
        self._watchFile()
        self.saveRequested.emit()

    @abstractmethod
    def saveACopy(self, filename):
        self._watchFile()
        self.saveRequested.emit()

    def encoding(self):
        return self.encoding_

    def size(self):
        if self.isNew:
            return 0
        else:
            return helper.get_size(self.filename)

    def modified(self):
        if self.isNew:
            return 0
        else:
            modifiedDateTime = QDateTime(datetime.fromtimestamp(os.path.getmtime(self.filename)))
            strDateTime = modifiedDateTime.toString(Qt.SystemLocaleShortDate)
            return unicode(strDateTime)

    def toJson(self):
        """Convert Document object to json string.
        :return: json string
        """
        class _Encoder(JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Document):
                    d = {'__class__': obj.__class__.__name__,
                         '__module__': obj.__module__}
                    # these attributes are not serializables
                    notSerializable = ('_Document__watcher',
                                       'stack',
                                       'sheet')
                    # get atributes dict to serialize
                    dictSerializable = {k:obj.__dict__[k] for k in obj.__dict__ if k not in notSerializable}
                    d.update(dictSerializable)
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
                    try:
                        module = __import__(module_name)
                        class_ = getattr(module, class_name)
                    # if exception occurred then module scope is current module
                    except:
                        module = sys.modules[module_name]
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
        self.canSave = True

    def new(self):
        super(Csv, self).new()

    # http://stackoverflow.com/questions/17245415/read-and-write-csv-files-including-unicode-with-python-2-7
    # https://github.com/jdunck/python-unicodecsv
    # https://nelsonslog.wordpress.com/2015/02/26/python-csv-benchmarks/
    def load(self, linesToLoad=-1):
        # detect encoding
        with io.open(self.filename, mode="rb") as f:
            data = f.read()
        detect = cchardet.detect(data)
        self.encoding_ = detect['encoding']
        # retrieve data
        data = []
        with io.open(self.filename, newline='', encoding=self.encoding_) as csvFile:    # Since Python 2.6, a good practice is to use io.open(),
                                                                                        # which also takes an encoding argument.
                                                                                        # if newline='' is not specified, newlines embedded inside quoted fields
                                                                                        # will not be interpreted correctly, and on platforms that use \r\n linendings
                                                                                        # on write an extra \r will be added. It should always be safe to specify
                                                                                        # newline='', since the csv module does its own (universal) newline handling.
            reader = csv.reader(csvFile,
                                delimiter=self.delimiter,
                                doublequote=self.doublequote,
                                escapechar = self.escapechar,
                                lineterminator= self.lineterminator,
                                quotechar=self.quotechar,
                                quoting=self.quoting,
                                skipinitialspace=self.skipinitialspace)
            if linesToLoad > -1:
                for line, row in enumerate(reader):
                    if line > linesToLoad:
                        break
                    data.append([QString(value) for value in row])
            else:
                for row in reader:
                    data.append([QString(value) for value in row])
        self.setArrayData(data)
        super(Csv, self).load()

    def save(self, newFilename=None):
        if newFilename:
            self.saveACopy(newFilename)
            self.filename = newFilename
        else:
            self.saveACopy(self.filename)
        self.commandClear()
        super(Csv, self).save(newFilename)

    def saveACopy(self, filename):
        self._unwatchFile()
        with io.open(filename, 'w', newline='', encoding=self.encoding_) as csvFile:
            writer = csv.writer(csvFile,
                                delimiter=self.delimiter,
                                doublequote=self.doublequote,
                                escapechar = self.escapechar,
                                lineterminator= self.lineterminator,
                                quotechar=self.quotechar,
                                quoting=self.quoting,
                                skipinitialspace=self.skipinitialspace)
            data = self.arrayData()
            for row in data:
                writer.writerow(row)
        super(Csv, self).saveACopy(filename)


class Xsl(Document):

    def __init__(self,
                 filename,
                 sheetname,
                 **kvparams):
        super(Xsl, self).__init__(filename)
        self.sheetname = sheetname
        self.canSave = False

    def new(self):
        pass

    def load(self, linesToLoad=-1):
        data = []
        wb = xlrd.open_workbook(self.filename)
        sh = wb.sheet_by_name(self.sheetname)
        for rownum in xrange(sh.nrows):
            for cell in sh.row(rownum):
                cell_type = cell.ctype
                cell_value = cell.value
                if cell_type == xlrd.XL_CELL_DATE:
                    # Returns a tuple.
                    get_col = xlrd.xldate.xldate_as_datetime(cell_value, wb.datemode)
                    #####dt_tuple = xlrd.xldate_as_tuple(cell_value, wb.datemode)
                    # Create datetime object from this tuple.
                    ######get_col = datetime.datetime(*dt_tuple)
                elif cell_type == xlrd.XL_CELL_NUMBER:
                    get_col = unicode(cell_value)
                else:
                    get_col = unicode(cell_value)
                print cell_value
                print get_col
                data.append(QString(unicode(get_col)))
## hay que 'pulir' la conversion de cualquier tipo a cadena
## self.data_.append([QString(value) for value in sh.row_values(rownum)])
## http://stackoverflow.com/questions/2739989/reading-numeric-excel-data-as-text-using-xlrd-in-python/2740525
## http://stackoverflow.com/questions/17827471/python-xlrd-discerning-dates-from-floats
###            self.data_.append([QString(unicode(value)) for value in sh.row_values(rownum)])
        self.setArrayData(data)
        super(Xsl, self).load()

    def save(self, newFilename=None):
        pass
