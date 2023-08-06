###############################################################################
#
# Worksheet - A class for writing the Excel XLSX Worksheet file.
#
# Copyright 2013, John McNamara, jmcnamara@cpan.org
#

# Standard packages.
import re
import datetime
from collections import defaultdict
from collections import namedtuple

# Package imports.
from . import xmlwriter
from .utility import xl_rowcol_to_cell
from .utility import xl_cell_to_rowcol


###############################################################################
#
# Decorator functions.
#
###############################################################################
def convert_cell_args(method):
    """
    Decorator function to convert A1 notation in cell method calls
    to the default row/col notation.

    """
    def cell_wrapper(self, *args):

        try:
            # First arg is an int, default to row/col notation.
            int(args[0])
            return method(self, *args)
        except ValueError:
            # First arg isn't an int, convert to A1 notation.
            new_args = list(xl_cell_to_rowcol(args[0]))
            new_args.extend(args[1:])
            return method(self, *new_args)

    return cell_wrapper


def convert_range_args(method):
    """
    Decorator function to convert A1 notation in range method calls
    to the default row/col notation.

    """
    def cell_wrapper(self, *args):

        try:
            # First arg is an int, default to row/col notation.
            int(args[0])
            return method(self, *args)
        except ValueError:
            # First arg isn't an int, convert to A1 notation.
            cell_1, cell_2 = args[0].split(':')
            row_1, col_1 = xl_cell_to_rowcol(cell_1)
            row_2, col_2 = xl_cell_to_rowcol(cell_2)
            new_args = [row_1, col_1, row_2, col_2]
            new_args.extend(args[1:])
            return method(self, *new_args)

    return cell_wrapper


def convert_column_args(method):
    """
    Decorator function to convert A1 notation in columns method calls
    to the default row/col notation.

    """
    def column_wrapper(self, *args):

        try:
            # First arg is an int, default to row/col notation.
            int(args[0])
            return method(self, *args)
        except ValueError:
            # First arg isn't an int, convert to A1 notation.
            cell_1, cell_2 = [col + '1' for col in args[0].split(':')]
            _, col_1 = xl_cell_to_rowcol(cell_1)
            _, col_2 = xl_cell_to_rowcol(cell_2)
            new_args = [col_1, col_2]
            new_args.extend(args[1:])
            return method(self, *new_args)

    return column_wrapper


###############################################################################
#
# Worksheet Class definition.
#
###############################################################################
class Worksheet(xmlwriter.XMLwriter):
    """
    A class for writing the Excel XLSX Worksheet file.

    """

    ###########################################################################
    #
    # Public API.
    #
    ###########################################################################

    def __init__(self):
        """
        Constructor.

        """

        super(Worksheet, self).__init__()

        self.name = None
        self.index = None
        self.str_table = None
        self.palette = None
        self.optimization = 0
        self.tempdir = None

        self.ext_sheets = []
        self.fileclosed = 0
        self.excel_version = 2007

        self.xls_rowmax = 1048576
        self.xls_colmax = 16384
        self.xls_strmax = 32767
        self.dim_rowmin = None
        self.dim_rowmax = None
        self.dim_colmin = None
        self.dim_colmax = None

        self.colinfo = []
        self.selections = []
        self.hidden = 0
        self.active = 0
        self.tab_color = 0

        self.panes = []
        self.active_pane = 3
        self.selected = 0

        self.page_setup_changed = 0
        self.paper_size = 0
        self.orientation = 1

        self.print_options_changed = 0
        self.hcenter = 0
        self.vcenter = 0
        self.print_gridlines = 0
        self.screen_gridlines = 1
        self.print_headers = 0

        self.header_footer_changed = 0
        self.header = ''
        self.footer = ''

        self.margin_left = 0.7
        self.margin_right = 0.7
        self.margin_top = 0.75
        self.margin_bottom = 0.75
        self.margin_header = 0.3
        self.margin_footer = 0.3

        self.repeat_rows = ''
        self.repeat_cols = ''
        self.print_area = ''

        self.page_order = 0
        self.black_white = 0
        self.draft_quality = 0
        self.print_comments = 0
        self.page_start = 0

        self.fit_page = 0
        self.fit_width = 0
        self.fit_height = 0

        self.hbreaks = []
        self.vbreaks = []

        self.protect = 0
        self.password = None

        self.set_cols = {}
        self.set_rows = {}

        self.zoom = 100
        self.zoom_scale_normal = 1
        self.print_scale = 100
        self.right_to_left = 0
        self.show_zeros = 1
        self.leading_zeros = 0

        self.outline_row_level = 0
        self.outline_col_level = 0
        self.outline_style = 0
        self.outline_below = 1
        self.outline_right = 1
        self.outline_on = 1
        self.outline_changed = 0

        self.default_row_height = 15
        self.default_row_zeroed = 0

        self.names = {}
        self.write_match = []
        self.table = defaultdict(dict)
        self.merge = []
        self.row_spans = {}

        self.has_vml = 0
        self.has_comments = 0
        self.comments = {}
        self.comments_array = []
        self.comments_author = ''
        self.comments_visible = 0
        self.vml_shape_id = 1024
        self.buttons_array = []

        self.autofilter = ''
        self.filter_on = 0
        self.filter_range = []
        self.filter_cols = {}

        self.col_sizes = {}
        self.row_sizes = {}
        self.col_formats = {}
        self.col_size_changed = 0
        self.row_size_changed = 0

        self.last_shape_id = 1
        self.rel_count = 0
        self.hlink_count = 0
        self.hlink_refs = []
        self.external_hyper_links = []
        self.external_drawing_links = []
        self.external_comment_links = []
        self.external_vml_links = []
        self.external_table_links = []
        self.drawing_links = []
        self.charts = []
        self.images = []
        self.tables = []
        self.sparklines = []
        self.shapes = []
        self.shape_hash = {}
        self.drawing = 0

        self.rstring = ''
        self.previous_row = 0

        self.validations = []
        self.cond_formats = {}
        self.dxf_priority = 1
        self.is_chartsheet = 0
        self.page_view = 0

        self.date_1904 = False
        self.epoch = datetime.datetime(1899, 12, 31)

    @convert_cell_args
    def write(self, row, col, *args):
        """
        Write data to a worksheet cell by calling the appropriate write_*()
        method based on the type of data being passed.

        Args:
            row:     The cell row (zero indexed).
            col:     The cell column (zero indexed).
            token:   Cell data.
            format:  An optional cell Format object.
            options: Any options to pass to sub function.

        Returns:
             0:    Success.
            -1:    Row or column is out of worksheet bounds.
            other: Return value of called method.

        """
        # Check the number of args passed.
        if not len(args):
            raise TypeError("write() takes at least 4 arguments (3 given)")

        # The first arg should be the token for all write calls.
        token = args[0]

        # Convert None to an empty string and thus a blank cell.
        if token is None:
            token = ''

        # Try work out the appropriate method to call.
        try:
            float(token)
            return self.write_number(row, col, *args)
        except:
            # Not a number. Continue to the checks below.
            pass

        # TODO. Add other write_* methods.
        if isinstance(token, datetime.datetime):
            return self.write_datetime(row, col, *args)
        elif token == '':
            return self.write_blank(row, col, *args)
        elif token.startswith('='):
            return self.write_formula(row, col, *args)
        else:
            return self.write_string(row, col, *args)

    @convert_cell_args
    def write_string(self, row, col, string, cell_format=None):
        """
        Write a string to a worksheet cell.

        Args:
            row:    The cell row (zero indexed).
            col:    The cell column (zero indexed).
            string: Cell data. Str.
            format: An optional cell Format object.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.
            -2: String truncated to 32k characters.

        """
        str_error = 0

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Check that the string is < 32767 chars.
        if len(string) > self.xls_strmax:
            string = string[:self.xls_strmax]
            str_error = -2

        # Write a shared string or an in-line string in optimisation mode.
        if self.optimization == 0:
            string_index = self.str_table._get_shared_string_index(string)
        else:
            string_index = string

        # Write previous row if in in-line string optimization mode.
        if self.optimization and row > self.previous_row:
            self._write_single_row(row)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('String', 'string, format')
        self.table[row][col] = cell_tuple(string_index, cell_format)

        return str_error

    @convert_cell_args
    def write_number(self, row, col, number, cell_format=None):
        """
        Write a number to a worksheet cell.

        Args:
            row:         The cell row (zero indexed).
            col:         The cell column (zero indexed).
            number:      Cell data. Int or float.
            cell_format: An optional cell Format object.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.

        """
        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Write previous row if in in-line string optimization mode.
        if self.optimization and row > self.previous_row:
            self._write_single_row(row)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('Number', 'number, format')
        self.table[row][col] = cell_tuple(number, cell_format)

        return 0

    @convert_cell_args
    def write_blank(self, row, col, blank, cell_format=None):
        """
        Write a blank cell with formatting to a worksheet cell. The blank
        token is ignored and the format only is written to the cell.

        Args:
            row:         The cell row (zero indexed).
            col:         The cell column (zero indexed).
            blank:       Any value. It is ignored.
            cell_format: An optional cell Format object.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.

        """
        # Don't write a blank cell unless it has a format.
        if cell_format is None:
            return 0

        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Write previous row if in in-line string optimization mode.
        if self.optimization and row > self.previous_row:
            self._write_single_row(row)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('Blank', 'format')
        self.table[row][col] = cell_tuple(cell_format)

        return 0

    @convert_cell_args
    def write_formula(self, row, col, formula, cell_format=None, value=0):
        """
        Write a formula to a worksheet cell.

        Args:
            row:         The cell row (zero indexed).
            col:         The cell column (zero indexed).
            formula:     Cell formula.
            cell_format: An optional cell Format object.
            value:       An optional value for the formula. Default is 0.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.

        """
        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Hand off array formulas.
        if formula.startswith('{') and formula.endswith('}'):
            return self.write_array_formula(row, col, row, col, formula,
                                            cell_format, value)

        # Remove the formula '=' sign if it exists.
        if formula.startswith('='):
            formula = formula.lstrip('=')

        # Write previous row if in in-line string optimization mode.
        if self.optimization and row > self.previous_row:
            self._write_single_row(row)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('Formula', 'formula, format, value')
        self.table[row][col] = cell_tuple(formula, cell_format, value)

        return 0

    @convert_range_args
    def write_array_formula(self, firstrow, firstcol, lastrow, lastcol,
                            formula, cell_format=None, value=0):
        """
        Write a formula to a worksheet cell.

        Args:
            firstrow:    The first row of the cell range. (zero indexed).
            firstcol:    The first column of the cell range.
            lastrow:     The last row of the cell range. (zero indexed).
            lastcol:     The last column of the cell range.
            formula:     Cell formula.
            cell_format: An optional cell Format object.
            value:       An optional value for the formula. Default is 0.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.

        """

        # Swap last row/col with first row/col as necessary.
        if firstrow > lastrow:
            firstrow, lastrow = lastrow, firstrow
        if firstcol > lastcol:
            firstcol, lastcol = lastcol, firstcol

        # Check that row and col are valid and store max and min values
        if self._check_dimensions(lastrow, lastcol):
            return -1

        # Define array range
        if firstrow == lastrow and firstcol == lastcol:
            cell_range = xl_rowcol_to_cell(firstrow, firstcol)
        else:
            cell_range = (xl_rowcol_to_cell(firstrow, firstcol) + ':'
                          + xl_rowcol_to_cell(lastrow, lastcol))

        # Remove array formula braces and the leading =.
        if formula[0] == '{':
            formula = formula[1:]
        if formula[0] == '=':
            formula = formula[1:]
        if formula[-1] == '}':
            formula = formula[:-1]

        # Write previous row if in in-line string optimization mode.
        if self.optimization and firstrow > self.previous_row:
            self._write_single_row(firstrow)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('ArrayFormula',
                                'formula, format, value, range')
        self.table[firstrow][firstcol] = cell_tuple(formula, cell_format,
                                                    value, cell_range)

        # Pad out the rest of the area with formatted zeroes.
        if not self.optimization:
            for row in range(firstrow, lastrow + 1):
                for col in range(firstcol, lastcol + 1):
                    if row != firstrow or col != firstcol:
                        self.write_number(row, col, 0, cell_format)

        return 0

    @convert_cell_args
    def write_datetime(self, row, col, date, cell_format):
        """
        Write a date to a worksheet cell.

        Args:
            row:         The cell row (zero indexed).
            col:         The cell column (zero indexed).
            date:        Date and/or time as a datetime object.
            cell_format: A cell Format object.

        Returns:
            0:  Success.
            -1: Row or column is out of worksheet bounds.

        """
        # Check that row and col are valid and store max and min values.
        if self._check_dimensions(row, col):
            return -1

        # Write previous row if in in-line string optimization mode.
        if self.optimization and row > self.previous_row:
            self._write_single_row(row)

        # Convert datetime to an Excel date.
        number = self._convert_date_time(date)

        # Store the cell data in the worksheet data table.
        cell_tuple = namedtuple('Number', 'number, format')
        self.table[row][col] = cell_tuple(number, cell_format)

        return 0

    def activate(self):
        """
        Set this worksheet as the active worksheet, i.e. the worksheet that is
        displayed when the workbook is opened. Also set it as selected.

        Note: An active worksheet cannot be hidden.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.hidden = 0
        self.selected = 1
        self.worksheet_meta.activesheet = self.index

    def select(self):
        """
        Set this worksheet as a selected worksheet, i.e. the worksheet
        has its tab highlighted.

        Note: A selected worksheet cannot be hidden.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.selected = 1
        self.hidden = 0

    @convert_column_args
    def set_column(self, firstcol, lastcol, width, cell_format=None,
                   options={}):
        """
        Set the width, and other properties of a single column or a
        range of columns.

        Args:
            firstcol:    First column (zero-indexed).
            lastcol:     Last column (zero-indexed). Can be same as firstcol.
            width:       Column width.
            cell_format: Column cell_format. (optional).
            options:     Dict of options such as hidden and level.

        Returns:
            0:  Success.
            -1: Column number is out of worksheet bounds.

        """
        # Ensure 2nd col is larger than first.
        if firstcol > lastcol:
            (firstcol, lastcol) = (lastcol, firstcol)

        # Don't modify the row dimensions when checking the columns.
        ignore_row = 1

        # Set optional column values.
        hidden = options.get('hidden', False)
        level = options.get('level', 0)

        # Store the column dimension only in some conditions.
        if cell_format or (width and hidden):
            ignore_col = 0
        else:
            ignore_col = 1

        # Check that each column is valid and store the max and min values.
        if self._check_dimensions(0, lastcol, ignore_row, ignore_col):
            return -1
        if self._check_dimensions(0, firstcol, ignore_row, ignore_col):
            return -1

        # Set the limits for the outline levels (0 <= x <= 7).
        if level < 0:
            level = 0
        if level > 7:
            level = 7

        if level > self.outline_col_level:
            self.outline_col_level = level

        # Store the column data.
        self.colinfo.append([firstcol, lastcol, width, cell_format, hidden,
                             level])

        # Store the column change to allow optimisations.
        self.col_size_changed = 1

        # Store the col sizes for use when calculating image vertices taking
        # hidden columns into account. Also store the column formats.

        # Set width to zero if col is hidden
        if hidden:
            width = 0

        for col in range(firstcol, lastcol + 1):
            self.col_sizes[col] = width
            if cell_format:
                self.col_formats[col] = cell_format

        return 0

    def set_row(self, row, height, cell_format=None, options={}):
        """
        Set the width, and other properties of a row.
        range of columns.

        Args:
            row:         Row number (zero-indexed).
            height:      Row width.
            cell_format: Row cell_format. (optional).
            options:     Dict of options such as hidden, level and collapsed.

        Returns:
            0:  Success.
            -1: Row number is out of worksheet bounds.

        """
        # Use minimum col in _check_dimensions().
        if self.dim_colmin is not None:
            min_col = self.dim_colmin
        else:
            min_col = 0

        # Check that row is valid.
        if self._check_dimensions(row, min_col):
            return -1

        if height is None:
            height = self.default_row_height

        # Set optional row values.
        hidden = options.get('hidden', False)
        collapsed = options.get('collapsed', False)
        level = options.get('level', 0)

        # If the height is 0 the row is hidden and the height is the default.
        if height == 0:
            hidden = 1
            height = self.default_row_height

        # Set the limits for the outline levels (0 <= x <= 7).
        if level < 0:
            level = 0
        if level > 7:
            level = 7

        if level > self.outline_row_level:
            self.outline_row_level = level

        # Store the row properties.
        self.set_rows[row] = [height, cell_format, hidden, level, collapsed]

        # Store the row change to allow optimisations.
        self.row_size_changed = 1

        # Store the row sizes for use when calculating image vertices.
        self.row_sizes[row] = height

    ###########################################################################
    #
    # Public API. Page Setup methods.
    #
    ###########################################################################
    def set_landscape(self):
        """
        Set the page orientation as landscape.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.orientation = 0
        self.page_setup_changed = 1

    def set_portrait(self):
        """
        Set the page orientation as portrait.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.orientation = 1
        self.page_setup_changed = 1

    def set_page_view(self):
        """
        Set the page view mode.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.page_view = 1

    def set_paper(self, paper_size):
        """
        Set the paper type. US Letter = 1, A4 = 9.

        Args:
            paper_size: Paper index.

        Returns:
            Nothing.

        """
        if paper_size:
            self.paper_size = paper_size
            self.page_setup_changed = 1

    def center_horizontally(self):
        """
        Center the page horizontally.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.print_options_changed = 1
        self.hcenter = 1

    def center_vertically(self):
        """
        Center the page vertically.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.print_options_changed = 1
        self.vcenter = 1

    def set_margins(self, left=0.7, right=0.7, top=0.75, bottom=0.75):
        """
        Set all the page margins in inches.

        Args:
            left:   Left margin.
            right:  Right margin.
            top:    Top margin.
            bottom: Bottom margin.

        Returns:
            Nothing.

        """
        self.margin_left = left
        self.margin_right = right
        self.margin_top = top
        self.margin_bottom = bottom

    def set_header(self, header='', margin=0.3):
        """
        Set the page header caption and optional margin.

        Args:
            header: Header string.
            margin: Header margin.

        Returns:
            Nothing.

        """
        if len(header) >= 255:
            raise Exception('Header string must be less than 255 characters')

        self.header = header
        self.margin_header = margin
        self.header_footer_changed = 1

    def set_footer(self, footer='', margin=0.3):
        """
        Set the page footer caption and optional margin.

        Args:
            footer: Footer string.
            margin: Footer margin.

        Returns:
            Nothing.

        """
        if len(footer) >= 255:
            raise Exception('Footer string must be less than 255 characters')

        self.footer = footer
        self.margin_footer = margin
        self.header_footer_changed = 1

    def hide_gridlines(self, option=1):
        """
        Set the option to hide gridlines on the screen and the printed page.

        Args:
            option:    0 : Don't hide gridlines
                       1 : Hide printed gridlines only
                       2 : Hide screen and printed gridlines

        Returns:
            Nothing.

        """
        if option == 0:
            self.print_gridlines = 1
            self.screen_gridlines = 1
            self.print_options_changed = 1
        elif option == 1:
            self.print_gridlines = 0
            self.screen_gridlines = 1
        else:
            self.print_gridlines = 0
            self.screen_gridlines = 0

    def print_across(self):
        """
        Set the order in which pages are printed.

        Args:
            None.

        Returns:
            Nothing.

        """
        self.page_order = 1
        self.page_setup_changed = 1

    ###########################################################################
    #
    # Private API.
    #
    ###########################################################################

    def _initialize(self, init_data):
        self.name = init_data['name']
        self.index = init_data['index']
        self.str_table = init_data['str_table']
        self.worksheet_meta = init_data['worksheet_meta']

    def _assemble_xml_file(self):
        # Assemble and write the XML file.

        # Write the XML declaration.
        self._xml_declaration()

        # Write the worksheet element.
        self._write_worksheet()

        # Write the dimension element.
        self._write_dimension()

        # Write the sheetViews element.
        self._write_sheet_views()

        # Write the sheetFormatPr element.
        self._write_sheet_format_pr()

        # Write the cols element.
        self._write_cols()

        # Write the printOptions element.
        self._write_print_options()

        # Write the sheetData element.
        self._write_sheet_data()

        # Write the pageMargins element.
        self._write_page_margins()

        # Write the pageSetup element.
        self._write_page_setup()

        # Write the headerFooter element.
        self._write_header_footer()

        # Close the worksheet tag.
        self._xml_end_tag('worksheet')

        # Close the file.
        self._xml_close()

    def _check_dimensions(self, row, col, ignore_row=False, ignore_col=False):
        # Check that row and col are valid and store the max and min
        # values for use in other methods/elements. The ignore_row /
        # ignore_col flags is used to indicate that we wish to perform
        # the dimension check without storing the value. The ignore
        # flags are use by set_row() and data_validate.

        # Check that the row/col are within the worksheet bounds.
        if row >= self.xls_rowmax or col >= self.xls_colmax:
            return -1

        # In optimization mode we don't change dimensions for rows
        # that are already written.
        if not ignore_row and not ignore_col and self.optimization == 1:
            if row < self.previous_row:
                return -1

        if not ignore_row:
            if self.dim_rowmin is None or row < self.dim_rowmin:
                self.dim_rowmin = row
            if self.dim_rowmax is None or row > self.dim_rowmax:
                self.dim_rowmax = row

        if not ignore_col:
            if self.dim_colmin is None or col < self.dim_colmin:
                self.dim_colmin = col
            if self.dim_colmax is None or col > self.dim_colmax:
                self.dim_colmax = col

        return 0

    def _convert_date_time(self, date):
        # Convert a Python datetime.datetime value to an Excel date number.
        delta = date - self.epoch
        excel_time = (delta.days
                      + (float(delta.seconds)
                      + float(delta.microseconds) / 1E6)
                      / (60 * 60 * 24))

        # Special case for datetime where time only has been specified and
        # the default date of 1900-01-01 is used.
        if date.isocalendar() == (1900, 1, 1):
            excel_time -= 1

        # Account for Excel erroneously treating 1900 as a leap year.
        if not self.date_1904 and delta.days > 59:
            excel_time += 1

        return excel_time

    def _options_changed(self):
        # Check to see if any of the worksheet options have changed.
        options_changed = 0
        print_changed = 0
        setup_changed = 0

        if (self.orientation == 0
                or self.hcenter == 1
                or self.vcenter == 1
                or self.header != ''
                or self.footer != ''
                or self.margin_header != 0.50
                or self.margin_footer != 0.50
                or self.margin_left != 0.75
                or self.margin_right != 0.75
                or self.margin_top != 1.00
                or self.margin_bottom != 1.00):
            setup_changed = 1

        # Special case for 1x1 page fit.
        if self.fit_width == 1 and self.fit_height == 1:
            options_changed = 1
            self.fit_width = 0
            self.fit_height = 0

        if (self.fit_width > 1
                or self.fit_height > 1
                or self.page_order == 1
                or self.black_white == 1
                or self.draft_quality == 1
                or self.print_comments == 1
                or self.paper_size != 0
                or self.print_scale != 100
                or self.print_gridlines == 1
                or self.print_headers == 1
                or self.hbreaks > 0
                or self.vbreaks > 0):
            print_changed = 1

        if (print_changed or setup_changed):
            options_changed = 1

        if self.screen_gridlines == 0:
            options_changed = 1
        if self.filter_on:
            options_changed = 1

        return (options_changed, print_changed, setup_changed)

    ###########################################################################
    #
    # XML methods.
    #
    ###########################################################################

    def _write_worksheet(self):
        # Write the <worksheet> element. This is the root element.

        schema = 'http://schemas.openxmlformats.org/'
        xmlns = schema + 'spreadsheetml/2006/main'
        xmlns_r = schema + 'officeDocument/2006/relationships'
        xmlns_mc = schema + 'markup-compatibility/2006'
        ms_schema = 'http://schemas.microsoft.com/'
        xmlns_x14ac = ms_schema + 'office/spreadsheetml/2009/9/ac'

        attributes = [
            ('xmlns', xmlns),
            ('xmlns:r', xmlns_r)]

        # Add some extra attributes for Excel 2010. Mainly for sparklines.
        if self.excel_version == 2010:
            attributes.append(('xmlns:mc', xmlns_mc))
            attributes.append(('xmlns:x14ac', xmlns_x14ac))
            attributes.append(('mc:Ignorable', 'x14ac'))

        self._xml_start_tag('worksheet', attributes)

    def _write_dimension(self):
        # Write the <dimension> element. This specifies the range of
        # cells in the worksheet. As a special case, empty
        # spreadsheets use 'A1' as a range.

        if self.dim_rowmin is None and self.dim_colmin is None:
            # If the min dimensions are not defined then no dimensions
            # have been set and we use the default 'A1'.
            ref = 'A1'

        elif self.dim_rowmin is None and self.dim_colmin is not None:
            # If the row dimensions aren't set but the column
            # dimensions are set then they have been changed via
            # set_column().

            if self.dim_colmin == self.dim_colmax:
                # The dimensions are a single cell and not a range.
                ref = xl_rowcol_to_cell(0, self.dim_colmin)
            else:
                # The dimensions are a cell range.
                cell_1 = xl_rowcol_to_cell(0, self.dim_colmin)
                cell_2 = xl_rowcol_to_cell(0, self.dim_colmax)
                ref = cell_1 + ':' + cell_2

        elif (self.dim_rowmin == self.dim_rowmax and
              self.dim_colmin == self.dim_colmax):
            # The dimensions are a single cell and not a range.
            ref = xl_rowcol_to_cell(self.dim_rowmin, self.dim_colmin)
        else:
            # The dimensions are a cell range.
            cell_1 = xl_rowcol_to_cell(self.dim_rowmin, self.dim_colmin)
            cell_2 = xl_rowcol_to_cell(self.dim_rowmax, self.dim_colmax)
            ref = cell_1 + ':' + cell_2

        self._xml_empty_tag('dimension', [('ref', ref)])

    def _write_sheet_views(self):
        # Write the <sheetViews> element.
        self._xml_start_tag('sheetViews')

        # Write the sheetView element.
        self._write_sheet_view()

        self._xml_end_tag('sheetViews')

    def _write_sheet_view(self):
        # Write the <sheetViews> element.
        attributes = []

        # Hide screen gridlines if required
        if not self.screen_gridlines:
            attributes.append(('showGridLines', 0))

        # Hide zeroes in cells.
        if not self.show_zeros:
            attributes.append(('showZeros', 0))

        # Display worksheet right to left for Hebrew, Arabic and others.
        if self.right_to_left:
            attributes.append(('rightToLeft', 1))

        # Show that the sheet tab is selected.
        if self.selected:
            attributes.append(('tabSelected', 1))

        # Turn outlines off. Also required in the outlinePr element.
        if not self.outline_on:
            attributes.append(("showOutlineSymbols", 0))

        # Set the page view/layout mode if required.
        if self.page_view:
            attributes.append(('view', 'pageLayout'))

        # Set the zoom level.
        if self.zoom != 100:
            if not self.page_view:
                attributes.append(('zoomScale', self.zoom))
                if self.zoom_scale_normal:
                    attributes.append(('zoomScaleNormal', self.zoom))

        attributes.append(('workbookViewId', 0))

        if self.panes or len(self.selections):
            self._xml_start_tag('sheetView', attributes)
            # self._write_panes()
            # self._write_selections()
            self._xml_end_tag('sheetView')
        else:
            self._xml_empty_tag('sheetView', attributes)

    def _write_sheet_format_pr(self):
        # Write the <sheetFormatPr> element.
        default_row_height = self.default_row_height

        attributes = [('defaultRowHeight', default_row_height)]

        self._xml_empty_tag('sheetFormatPr', attributes)

    def _write_cols(self):
        # Write the <cols> element and <col> sub elements.

        # Exit unless some column have been formatted.
        if not self.colinfo:
            return

        self._xml_start_tag('cols')

        for col_info in self.colinfo:
            self._write_col_info(col_info)

        self._xml_end_tag('cols')

    def _write_col_info(self, col_info):
        # Write the <col> element.

        col_min, col_max, width, cell_format, hidden, level = col_info
        collapsed = 0
        custom_width = 1
        xf_index = 0

        # Get the cell_format index.
        if cell_format:
            xf_index = cell_format._get_xf_index()

        # Set the Excel default column width.
        if width is None:
            if not hidden:
                width = 8.43
                custom_width = 0
            else:
                width = 0
        elif width == 8.43:
            # Width is defined but same as default.
            custom_width = 0

        # Convert column width from user units to character width.
        if width > 0:
            # For Calabri 11.
            max_digit_width = 7
            padding = 5
            width = int((float(width) * max_digit_width + padding)
                        / max_digit_width * 256.0) / 256.0

        attributes = [
            ('min', col_min + 1),
            ('max', col_max + 1),
            ('width', width)]

        if xf_index:
            attributes.append(('style', xf_index))
        if hidden:
            attributes.append(('hidden', '1'))
        if custom_width:
            attributes.append(('customWidth', '1'))
        if level:
            attributes.append(('outlineLevel', level))
        if collapsed:
            attributes.append(('collapsed', '1'))

        self._xml_empty_tag('col', attributes)

    def _write_sheet_data(self):
        # Write the <sheetData> element.

        if self.dim_rowmin is None:
            # If the dimensions aren't defined there is no data to write.
            self._xml_empty_tag('sheetData')
        else:
            self._xml_start_tag('sheetData')
            self._write_rows()
            self._xml_end_tag('sheetData')

    def _write_page_margins(self):
        # Write the <pageMargins> element.
        attributes = [
            ('left', self.margin_left),
            ('right', self.margin_right),
            ('top', self.margin_top),
            ('bottom', self.margin_bottom),
            ('header', self.margin_header),
            ('footer', self.margin_footer)]

        self._xml_empty_tag('pageMargins', attributes)

    def _write_page_setup(self):
        # Write the <pageSetup> element.
        #
        # The following is an example taken from Excel.
        #
        # <pageSetup
        #     paperSize="9"
        #     scale="110"
        #     fitToWidth="2"
        #     fitToHeight="2"
        #     pageOrder="overThenDown"
        #     orientation="portrait"
        #     blackAndWhite="1"
        #     draft="1"
        #     horizontalDpi="200"
        #     verticalDpi="200"
        #     r:id="rId1"
        # />
        #
        attributes = []

        # Skip this element if no page setup has changed.
        if not self.page_setup_changed:
            return

        # Set paper size.
        if self.paper_size:
            attributes.append(('paperSize', self.paper_size))

        # Set the print_scale.
        if self.print_scale != 100:
            attributes.append(('scale', self.print_scale))

        # Set the "Fit to page" properties.
        if self.fit_page and self.fit_width != 1:
            attributes.append(('fitToWidth', self.fit_width))

        if self.fit_page and self.fit_height != 1:
            attributes.append(('fitToHeight', self.fit_height))

        # Set the page print direction.
        if self.page_order:
            attributes.append(('pageOrder', "overThenDown"))

        # Set page orientation.
        if self.orientation:
            attributes.append(('orientation', 'portrait'))
        else:
            attributes.append(('orientation', 'landscape'))

        self._xml_empty_tag('pageSetup', attributes)

    def _write_print_options(self):
        # Write the <printOptions> element.
        attributes = []

        if not self.print_options_changed:
            return

        # Set horizontal centering.
        if self.hcenter:
            attributes.append(('horizontalCentered', 1))

        # Set vertical centering.
        if self.vcenter:
            attributes.append(('verticalCentered', 1))

        # Enable row and column headers.
        if self.print_headers:
            attributes.append(('headings', 1))

        # Set printed gridlines.
        if self.print_gridlines:
            attributes.append(('gridLines', 1))

        self._xml_empty_tag('printOptions', attributes)

    def _write_header_footer(self):
        # Write the <headerFooter> element.

        if not self.header_footer_changed:
            return

        self._xml_start_tag('headerFooter')

        if self.header:
            self._write_odd_header()
        if self.footer:
            self._write_odd_footer()

        self._xml_end_tag('headerFooter')

    def _write_odd_header(self):
        # Write the <headerFooter> element.
        self._xml_data_element('oddHeader', self.header)

    def _write_odd_footer(self):
        # Write the <headerFooter> element.
        self._xml_data_element('oddFooter', self.footer)

    def _write_rows(self):
        # Write out the worksheet data as a series of rows and cells.
        self._calculate_spans()

        for row_num in range(self.dim_rowmin, self.dim_rowmax + 1):

            if (row_num in self.set_rows or row_num in self.comments
                    or self.table[row_num]):
                # Only process rows with formatting, cell data and/or comments.

                span_index = int(row_num / 16)

                if span_index in self.row_spans:
                    span = self.row_spans[span_index]
                else:
                    span = None

                if self.table[row_num]:
                    # Write the cells if the row contains data.
                    if row_num not in self.set_rows:
                        self._write_row(row_num, span)
                    else:
                        self._write_row(row_num, span, self.set_rows[row_num])

                    for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                        if col_num in self.table[row_num]:
                            col_ref = self.table[row_num][col_num]
                            self._write_cell(row_num, col_num, col_ref)

                    self._xml_end_tag('row')

                elif row_num in self.comments:
                    # Row with comments in cells.
                    self._write_empty_row(row_num, span,
                                          self.set_rows[row_num])
                else:
                    # Blank row with attributes only.
                    self._write_empty_row(row_num, span,
                                          self.set_rows[row_num])

    def _write_single_row(self, current_row_num):
        # Write out the worksheet data as a single row with cells.
        # This method is used when memory optimisation is on. A single
        # row is written and the data table is reset. That way only
        # one row of data is kept in memory at any one time. We don't
        # write span data in the optimised case since it is optional.

        # Set the new previous row as the current row.
        row_num = self.previous_row
        self.previous_row = current_row_num

        if (row_num in self.set_rows or row_num in self.comments
                or self.table[row_num]):
            # Only process rows with formatting, cell data and/or comments.

            # No span data in optimised mode.
            span = None

            if self.table[row_num]:
                # Write the cells if the row contains data.
                if row_num not in self.set_rows:
                    self._write_row(row_num, span)
                else:
                    self._write_row(row_num, span, self.set_rows[row_num])

                for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                    if col_num in self.table[row_num]:
                        col_ref = self.table[row_num][col_num]
                        self._write_cell(row_num, col_num, col_ref)

                self._xml_end_tag('row')
            else:
                # Row attributes or comments only.
                self._write_empty_row(row_num, span, self.set_rows[row_num])

        # Reset table.
        self.table.clear()

    def _calculate_spans(self):
        # Calculate the "spans" attribute of the <row> tag. This is an
        # XLSX optimisation and isn't strictly required. However, it
        # makes comparing files easier. The span is the same for each
        # block of 16 rows.
        spans = {}
        span_min = None
        span_max = None

        for row_num in range(self.dim_rowmin, self.dim_rowmax + 1):

            if row_num in self.table:
                # Calculate spans for cell data.
                for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                    if col_num in self.table[row_num]:
                        if span_min is None:
                            span_min = col_num
                            span_max = col_num
                        else:
                            if col_num < span_min:
                                span_min = col_num
                            if col_num > span_max:
                                span_max = col_num

            if row_num in self.comments:
                # Calculate spans for comments.
                for col_num in range(self.dim_colmin, self.dim_colmax + 1):
                    if self.comments[row_num][col_num] is not None:

                        if span_min is None:
                            span_min = col_num
                            span_max = col_num
                        else:
                            if col_num < span_min:
                                span_min = col_num
                            if col_num > span_max:
                                span_max = col_num

            if ((row_num + 1) % 16 == 0) or row_num == self.dim_rowmax:
                span_index = int(row_num / 16)

                if span_min is not None:
                    span_min += 1
                    span_max += 1
                    spans[span_index] = "%s:%s" % (span_min, span_max)
                    span_min = None

        self.row_spans = spans

    def _write_row(self, row, spans, properties=None, empty_row=False):
        # Write the <row> element.
        xf_index = 0

        if properties:
            height, cell_format, hidden, level, collapsed = properties
        else:
            height, cell_format, hidden, level, collapsed = 15, None, 0, 0, 0

        if height is None:
            height = self.default_row_height

        attributes = [('r', row + 1)]

        # Get the cell_format index.
        if cell_format:
            xf_index = cell_format._get_xf_index()

        # Add row attributes where applicable.
        if spans:
            attributes.append(('spans', spans))
        if xf_index:
            attributes.append(('s', xf_index))
        if cell_format:
            attributes.append(('customFormat', 1))
        if height != 15:
            attributes.append(('ht', height))
        if hidden:
            attributes.append(('hidden', 1))
        if height != 15:
            attributes.append(('customHeight', 1))
        if level:
            attributes.append(('outlineLevel', level))
        if collapsed:
            attributes.append(('collapsed', 1))
        if self.excel_version == 2010:
            attributes.append(('x14ac:dyDescent', '0.25'))

        if empty_row:
            self._xml_empty_tag_unencoded('row', attributes)
        else:
            self._xml_start_tag_unencoded('row', attributes)

    def _write_empty_row(self, *args):
        # Write and empty <row> element.
        self._write_row(*args, empty_row=True)

    def _write_cell(self, row, col, cell):
        # Write the <cell> element.
        #
        # Note. This is the innermost loop so efficiency is important.
        cell_range = xl_rowcol_to_cell(row, col)

        attributes = [('r', cell_range)]

        if cell.format:
            # Add the cell format index.
            xf_index = cell.format._get_xf_index()
            attributes.append(('s', xf_index))
        elif row in self.set_rows and self.set_rows[row][1]:
            # Add the row format.
            row_xf = self.set_rows[row][1]
            attributes.append(('s', row_xf._get_xf_index()))
        elif col in self.col_formats:
            # Add the column format.
            col_xf = self.col_formats[col]
            attributes.append(('s', col_xf._get_xf_index()))

        # Write the various cell types.
        if type(cell).__name__ == 'Number':
            # Write a number.
            self._xml_number_element(cell.number, attributes)

        elif type(cell).__name__ == 'String':
            # Write a string.
            string = cell.string

            if not self.optimization:
                # Write a shared string.
                self._xml_string_element(string, attributes)
            else:
                # Write an optimised in-line string.

                # TODO: Fix control char encoding when unit test is ported.
                # Escape control characters. See SharedString.pm for details.
                # string =~ s/(_x[0-9a-fA-F]{4}_)/_x005F1/g
                # string =~s/([\x00-\x08\x0B-\x1F])/sprintf "_x04X_", ord(1)/eg

                # Write any rich strings without further tags.
                if re.search('^<r>', string) and re.search('</r>$', string):
                    self._xml_rich_inline_string(string, attributes)
                else:
                    # Add attribute to preserve leading or trailing whitespace.
                    preserve = 0
                    if re.search('^\s', string) or re.search('\s$', string):
                        preserve = 1

                    self._xml_inline_string(string, preserve, attributes)

        elif type(cell).__name__ == 'Formula':
            # Write a formula. First check if the formula value is a string.
            try:
                float(cell.value)
            except ValueError:
                attributes.append(('t', 'str'))

            self._xml_formula_element(cell.formula, cell.value, attributes)

        elif type(cell).__name__ == 'ArrayFormula':
            # Write a array formula.

            # First check if the formula value is a string.
            try:
                float(cell.value)
            except ValueError:
                attributes.append(('t', 'str'))

            # Write an array formula.
            self._xml_start_tag('c', attributes)
            self._write_cell_array_formula(cell.formula, cell.range)
            self._write_cell_value(cell.value)
            self._xml_end_tag('c')

        elif type(cell).__name__ == 'Blank':
            # Write a empty cell.
            self._xml_empty_tag('c', attributes)

    def _write_cell_value(self, value):
        # Write the cell value <v> element.
        if value is None:
            value = ''

        self._xml_data_element('v', value)

    def _write_cell_array_formula(self, formula, cell_range):
        # Write the cell array formula <f> element.
        attributes = [
            ('t', 'array'),
            ('ref', cell_range)
        ]

        self._xml_data_element('f', formula, attributes)
