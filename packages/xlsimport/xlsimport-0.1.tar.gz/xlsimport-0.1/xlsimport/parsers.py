# -*- coding: utf-8 -*-
from xlrd.xldate import XLDateError
from dateutil.parser import parse
import datetime
import re
import xlrd
try:
    from django.core.exceptions import ValidationError
    from django.utils.translation import ugettext as _
except ImportError:
    import gettext as _

    class ValidationError(Exception):
        pass

XL_CELL_EMPTY = 0   # empty string u''
XL_CELL_TEXT = 1    # a Unicode string
XL_CELL_NUMBER = 2  # float
XL_CELL_DATE = 3    # float
XL_CELL_BOOLEAN = 4 # int; 1 means TRUE, 0 means FALSE
XL_CELL_ERROR = 5   # int representing internal Excel codes; for a text representation, refer to the supplied dictionary error_text_from_code
XL_CELL_BLANK = 6   # empty string u''. Note: this type will appear only when open_workbook(..., formatting_info=True) is used.


class CellParser(object):
    parser_type = None

    def __init__(self, value, datemode):
        self.value = value
        self.datemode = datemode

    def to_python(self):
        """return python object or raise ValidationError"""
        raise NotImplementedError('Override this method in children class')


class DateCellToDateParser(CellParser):
    """Parse Date cell into date"""
    parser_type = XL_CELL_DATE

    def to_python(self):
        try:
            date = xlrd.xldate_as_tuple(
                int(float(self.value)), int(self.datemode))
            date = datetime.date(date[0],
                date[1], date[2])
        except (ValueError, AttributeError, UnicodeError, XLDateError,
            IndexError):
            raise ValidationError(_('Wrong cell format, expected date'))
        else:
            return date


class NumberCellToIntParser(CellParser):
    """Parse number cell into integer"""
    parser_type = XL_CELL_NUMBER

    def to_python(self):
        if self.value - int(self.value):
            raise ValidationError(_('The field required to be a real number without fractional part'))
        else:
            return int(self.value)


class NumberCellToFloatParser(CellParser):
    """Parse text cell into float"""
    parser_type = XL_CELL_NUMBER

    def to_python(self):
        try:
            if self.value - int(self.value):
                return u'%s' % self.value
            else:
                return u'%d' % int(self.value)
        except (TypeError, ValueError):
            raise ValidationError(_('The field required to be a number'))

class NumberCellToStringParser(CellParser):
    """Parse number cell into text"""
    parser_type = XL_CELL_NUMBER

    def to_python(self):
        try:
            return u'%d' % self.value
        except (TypeError, ValueError):
            raise ValidationError(_('The field required to be a number'))


class TextCellToStringParser(CellParser):
    """Parse text cell into string"""
    parser_type = XL_CELL_TEXT

    def to_python(self):
        text = self.value
        text = re.sub("\n", ' ', text)
        text = re.sub("\s\s+", ' ', text)
        text = text.strip()
        return text


class TextCellToIntParser(CellParser):
    """Parse text cell to int"""
    parser_type = XL_CELL_TEXT

    def to_python(self):
        text = self.value
        text = re.sub("\n", '', text)
        text = re.sub("\s", '', text)
        try:
            number = int(text)
        except ValueError:
            raise ValidationError(_("The cell required to contain number"))
        else:
            return number


class TextCellToDateParser(CellParser):
    """Parse text cell with date into date"""
    parser_type = XL_CELL_TEXT

    def to_python(self):
        try:
            date = parse(self.value)
        except ValueError:
            raise  ValidationError(_('Unrecognized date format'))
        else:
            return date


class TextCellRegexpParser(CellParser):
    """Parse text with regexp"""
    parser_type = XL_CELL_TEXT
    regexp_list = []

    def to_python(self):
        if any([re.match(regexp, self.value, re.UNICODE)
            for regexp in self.regexp_list]):
            return self.value
        else:
            raise ValidationError(_('The field does not match required pattern'))


class EmptyCellDummyParser(CellParser):
    """Requires cell to be empty"""
    parser_type = XL_CELL_EMPTY

    def to_python(self):
        pass


class BlankCellDummyParser(CellParser):
    """Requires blank cell"""
    parser_type = XL_CELL_BLANK

    def to_python(self):
        pass


class DateCellDummyParser(CellParser):
    """Requires cell to have date format"""
    parser_type = XL_CELL_DATE

    def to_python(self):
        pass


class TextCellDummyParser(CellParser):
    """Requires cell to text"""
    parser_type = XL_CELL_TEXT

    def to_python(self):
        pass


class NumberCellDummyParser(CellParser):
    """Requires cell to be number"""
    parser_type = XL_CELL_NUMBER

    def to_python(self):
        pass


dummy_parsers = (EmptyCellDummyParser, BlankCellDummyParser,
    DateCellDummyParser, TextCellDummyParser, NumberCellDummyParser)
blank_parsers = (BlankCellDummyParser, EmptyCellDummyParser)
