#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" ttkCalendar widget (written by Guilherme Polo, 2008.) 
    with additional controls 
"""

# pytkapp.tkw: ttkCalendar widget with additional controls
#
# Copyright (c) 2013 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

###################################
## import
###################################
import sys

import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext     

if    sys.hexversion >= 0x03000000:
    from tkinter import Canvas, Toplevel, Button
    from tkinter.constants import E, YES, BOTH
    import tkinter.font as tkfont
    import tkinter.ttk as ttk
else:
    from Tkinter import Canvas, Toplevel, Button  
    from Tkconstants import E, YES, BOTH
    import tkFont as tkfont
    import ttk as ttk

import calendar
import datetime
import locale
import re

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)
        
from pytkapp.pta_routines import get_estr, xprint
from pytkapp.tkw.tkw_routines import toplevel_footer

ALLOWED_DATE_FORMATS = ('dd.mm.yyyy', 'yyyy.mm.dd', 'mm.dd.yyyy', 'yyyy.dd.mm',\
                        'dd-mm-yyyy', 'yyyy-mm-dd', 'mm-dd-yyyy', 'yyyy-dd-mm'\
                        'dd/mm/yyyy', 'yyyy/mm/dd', 'mm/dd/yyyy', 'yyyy/dd/mm')
DATETIME_MAP = {}
for fmt in ALLOWED_DATE_FORMATS:
    DATETIME_MAP[fmt] = fmt.replace('dd','%d').replace('mm','%m').replace('yyyy','%Y')

###################################
## routines
###################################
def validate_date(pv_value, pv_format='dd.mm.yyyy'):
    """ validate string with date and return it

        return None or datetime
        or raise ValueError
    """

    lv_out = None

    lv_year = ''
    lv_month = ''
    lv_day = ''

    lv_separator = re.sub('\d', '', pv_value)
    if len(lv_separator) > 1 and re.sub(lv_separator[:1], '', lv_separator) != '':
        raise ValueError('Only one type of separator are allowed !')
    elif len(lv_separator) == 0:
        raise ValueError('Value must contain separator !')
    else:
        lv_separator = lv_separator[:1]

    if pv_value.find(lv_separator) == -1:
        raise ValueError('Invalid format')

    ll_components = pv_format.split(lv_separator)
    if len(ll_components) != 3:
        raise ValueError('Format must contain 3 groups (d,m,y)')

    lv_pattern = ''
    if lv_separator == '.':
        lv_patseparator = '\.'
    else:
        lv_patseparator = lv_separator

    for component in ll_components:
        lv_letter = component[:1].lower()
        if lv_letter == 'd':
            lv_name = 'day'
        elif lv_letter == 'm':
            lv_name = 'month'
        elif lv_letter == 'y':
            lv_name = 'year'
        else:
            raise ValueError('Invalid format')

        lv_pattern += '(?P<%s>\d{%s,})%s' % (lv_name, len(component), lv_patseparator)

    lv_pattern = lv_pattern.rstrip(lv_patseparator)

    try:
        lo_search = re.search(lv_pattern, pv_value)
    except re.error:
        raise ValueError
    else:
        if lo_search is not None:
            ld_data = lo_search.groupdict()

            lv_day = ld_data['day']
            if lv_day.isdigit():
                lv_day = int(lv_day)
            else:
                raise ValueError
            lv_month = ld_data['month']
            if lv_month.isdigit():
                lv_month = int(lv_month)
            else:
                raise ValueError
            lv_year = ld_data['year']
            if lv_year.isdigit():
                lv_year = int(lv_year)
            else:
                raise ValueError
            
            if not 0 < lv_day < 32:
                raise ValueError
            elif not 0 < lv_month < 13:
                raise ValueError
            elif not 0 < lv_year < 10000:
                raise ValueError

            lv_out = datetime.date(lv_year, lv_month, lv_day)
        else:
            lv_out = None

    return lv_out

def show_calendar(pw_master, **kw):
    """ call calendar window """
    
    lv_out = None
    
    try:
        top_page = Toplevel( pw_master )
        top_page.withdraw()
        top_page.lift()
        
        top_page.title(_('Select date'))
        top_page.protocol("WM_DELETE_WINDOW", top_page.destroy)

        top_page.transient( pw_master )

        ttkcal = ttkCalendar(top_page,
                             **kw)
        ttkcal.pack(expand=YES, fill=BOTH)

        b = Button( top_page, text = _('Close'), command = top_page.destroy )
        b.pack(expand=1, anchor=E)

        toplevel_footer( top_page, pw_master )

        lv_out = ttkcal.selection
                
        ttkcal.destroy()
    except:
        lv_message = 'Failed to show calendar: %s' % (get_estr())
        xprint(lv_message)
        
    return lv_out

###################################
## classes
###################################
class ttkCalendar(ttk.Frame):
    """Simple calendar using ttk Treeview together with calendar and datetime
    classes.
    
    written by Guilherme Polo, 2008.
    """    
    ###October 2012: Paul "Mid.Tier" some changes mid.tier@gmail.com

    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, **kw):
        """
        WIDGET-SPECIFIC OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground
        """
        # remove custom options from kw before initializating ttk.Frame
        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale_ = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', '#ecffc4')
        sel_fg = kw.pop('selectforeground', '#05640e')
        
        self._outformat = kw.pop('outformat', None)
        self._locale = locale_
        
        self._date = self.datetime(year, month, 1)
        self._selection = None # no date selected

        ttk.Frame.__init__(self, master, **kw)

        self._cal = self.create_calendar(locale_, fwday)

        self.__setup_styles()       # creates custom styles
        self.__place_widgets()      # pack/grid used widgets
        self.__config_calendar()    # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self.__setup_selection(sel_bg, sel_fg)

        # store items ids, used for insertion later
        self._items = [self._calendar.insert('', 'end', values='') for i in range(6)]
        # insert dates in the currently empty calendar
        self._build_calendar()

        # set the minimal size for the widget
        self._calendar.bind('<Map>', self.__minsize)
        
    def create_calendar(self, locale_, fwday):
        # initialize proper calendar class
        
        if locale_ is None:
            return calendar.TextCalendar(fwday)
        else:
            return calendar.LocaleTextCalendar(fwday, locale_)        

    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )

        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))
        style.layout('D.TButton', arrow_layout('down'))
        style.layout('U.TButton', arrow_layout('up'))

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lybtn = ttk.Button(hframe, style='D.TButton', command=self._prev_year)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._prev_month)
        rbtn = ttk.Button(hframe, style='R.TButton', command=self._next_month)
        rybtn = ttk.Button(hframe, style='U.TButton', command=self._next_year)
        self._header = ttk.Label(hframe, width=15, anchor='center')
        # the calendar
        self._calendar = ttk.Treeview(self, show='', selectmode='none', height=7)

        # pack the widgets
        hframe.pack(in_=self, side='top', pady=4, anchor='center')
        lybtn.grid(in_=hframe)
        lbtn.grid(in_=hframe, column=1, row=0)
        self._header.grid(in_=hframe, column=2, row=0, padx=12)
        rbtn.grid(in_=hframe, column=3, row=0)
        rybtn.grid(in_=hframe, column=4, row=0)
        #self._calendar.pack(in_=self, expand=1, fill='both', side='bottom')
        self._calendar.pack(expand=1, fill='both', side='bottom')

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        
        if self._locale == '':
            for i in range(len(cols)):
                col = cols[i]
                try:
                    cols[i] = col.decode(locale.getpreferredencoding())        
                except:
                    cols[i] = col

        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='grey90')
        self._calendar.insert('', 'end', values=cols, tag='header')
        # adjust its columns width
        font = tkfont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                                  anchor='e')

    def __setup_selection(self, sel_bg, sel_fg):
        def _forget():
            canvas.place_forget()
            self._selection = None

        self._font = tkfont.Font()
        self._canvas = canvas = Canvas(self._calendar,
                                       background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')

        canvas.bind('<ButtonPress-1>', lambda evt: _forget())
        self._calendar.bind('<Configure>', lambda evt: canvas.place_forget())
        self._calendar.bind('<ButtonPress-1>', self._pressed)

    def __minsize(self, evt):
        width, height = self.master.geometry().split('x')
        height = height[:height.index('+')]
        self.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)

        if self._locale == '':
            try:
                header = header.decode(locale.getpreferredencoding())        
            except:
                pass
        
        self._header['text'] = header.title()

        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)
        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self._calendar.item(item, values=fmt_week)

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox

        textw = self._font.measure(text)

        canvas = self._canvas
        canvas.configure(width=width, height=height)
        canvas.coords(canvas.text, width - textw, height / 2 - 1)
        canvas.itemconfigure(canvas.text, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)

    # Callbacks
    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or not item in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)['values']
        if not len(item_values): # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text: # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox: # calendar not visible yet
            return

        # update and then show selection
        text = '%02d' % text
        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar() # reconstuct calendar

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar() # reconstruct calendar


    def _prev_year(self):
        """Updated calendar to show the previous year."""
        self._canvas.place_forget()

        self._date = self._date - self.timedelta(weeks=52)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        self._build_calendar() # reconstuct calendar

    def _next_year(self):
        """Update calendar to show the next year."""
        self._canvas.place_forget()

        year, month = self._date.year, self._date.month
        self._date = self.datetime(self._date.year+1, self._date.month, 1)
        self._build_calendar() # reconstruct calendar       

    # Properties

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        if self._outformat is None:
            return self.datetime(year, month, int(self._selection[0]))
        else:
            return self.datetime(year, month, int(self._selection[0])).strftime(self._outformat)

            