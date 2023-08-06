# coding=utf-8
try:
    from django.core.exceptions import ValidationError
    from django.utils.translation import ugettext as _
except ImportError:
    import gettext as _

    class ValidationError(Exception):
        pass


class CellParserMismatch(Exception):

    def __init__(self):
        self.messages = [_('Field type mismatch'), ]

class ErrorRow(list):

    def __init__(self, data, index, logic_exception=None):
        self.row_index = index
        self.logic_exception = logic_exception
        super(ErrorRow, self).__init__(data)

class CellParser(object):
    parser_type = None

    def __init__(self, value, datemode):
        self.value = value
        self.datemode = datemode

    def to_python(self):
        """return python object or raise ValidationError"""
        raise NotImplementedError('Override this method in children class')

class Format(object):

    cells = []  # override this

    # xls reading options
    start_line = 0
    sheet_num = 0

    def __init__(self, document, name=None):
        """
        name - internal format name
        cell_parser - iterable object, contains row cells for validation
        for example:
            [(cell1,),
             (cell2,),
             (cell3_1, cell3_2),
             (cell4,)]
        If validation in cell3_1 fails, format will try to validate cell3_2.
        """
        self.name = name
        self.document = document
        self.cell_data = []
        self.sheet = self.document.sheet_by_index(self.sheet_num)

    def to_python(self, data_row):
        """
        Returns python object with all required data
        Object should not expect any Exception subclasses in data_row
        Should return tuple of objects:
            userprofile, document_numner, etc...
        """
        raise NotImplementedError('Override this method in children class')

    def _run_cell_parser(self, cell_parser, cell_data):
        """Validate cell data through parser"""
        if cell_parser.parser_type == cell_data.ctype:
            return cell_parser(cell_data.value, self.document.datemode).to_python()
        else:
            raise CellParserMismatch()

    def __iter__(self):
        return self.next()

    def next(self):
        # per-row validation
        for rownum in range(self.start_line, self.sheet.nrows):
            data_row = self.sheet.row_slice(rownum)[:len(self.cells)]
            parsed_data = []

            # per-cell validation
            for i, cell_data in enumerate(data_row):
                # temp variables
                exception = None
                value = None
                ok = False  # bool if any value returned
                # run all parsers
                for cell_parser in self.cells[i]['parsers']:
                    try:
                        value = self._run_cell_parser(cell_parser, cell_data)
                        ok = True
                        break
                    except ValidationError, e:
                        if exception is None:
                            exception = e
                        else:
                            pass  # go to next cellparser
                    except CellParserMismatch:
                        pass  # go to next cellparser

                # store value and exception data
                if (not ok) and (exception is None):
                    exception = CellParserMismatch()
                if ok:
                    parsed_data.append(value)
                else:
                    parsed_data.append(exception)

            yield parsed_data
