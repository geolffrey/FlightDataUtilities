from __future__ import print_function, unicode_literals

import math
import operator
import re

from io import StringIO
from functools import reduce
from six.moves import zip_longest


# http://code.activestate.com/recipes/267662/

def indent(rows, hasHeader=False, headerChar='-', delim=' | ', justify='left',
           separateRows=False, prefix='', postfix='', wrapfunc=lambda x:x):
    """Indents a table by column.
       - rows: A sequence of sequences of items, one sequence per row.
       - hasHeader: True if the first row consists of the columns' names.
       - headerChar: Character to be used for the row separator line
         (if hasHeader==True or separateRows==True).
       - delim: The column delimiter.
       - justify: Determines how are data justified in their column.
         Valid values are 'left','right' and 'center'.
       - separateRows: True if rows are to be separated by a line
         of 'headerChar's.
       - prefix: A string prepended to each printed row.
       - postfix: A string appended to each printed row.
       - wrapfunc: A function f(text) for wrapping text; each element in
         the table is first wrapped by this function."""
    # closure for breaking logical rows to physical, using wrapfunc
    def rowWrapper(row):
        newRows = [wrapfunc(item).split('\n') for item in row]
        return [[substr or '' for substr in item] for item in zip_longest(*newRows)]
    # break each logical row into one or more physical ones
    logicalRows = [rowWrapper(row) for row in rows]
    # columns of physical rows
    columns = zip_longest(*reduce(operator.add,logicalRows))
    # get the maximum of each column by the string length of its items
    maxWidths = [max([len(str(item)) for item in column]) for column in columns]
    rowSeparator = headerChar * (len(prefix) + len(postfix) + sum(maxWidths) + \
                                 len(delim)*(len(maxWidths)-1))
    # select the appropriate justify method
    justify = {'center':str.center, 'right':str.rjust, 'left':str.ljust}[justify.lower()]
    output = StringIO()
    if separateRows:
        output.write(rowSeparator)
    for physicalRows in logicalRows:
        for row in physicalRows:
            output.write(
                prefix
                + delim.join([justify(str(item),width) for (item,width) in zip(row,maxWidths)])
                + postfix)
        if separateRows or hasHeader:
            output.write(rowSeparator)
            hasHeader=False
    return output.getvalue()

# written by Mike Brown
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/148061
def wrap_onspace(text, width, carriage_return='\n'):
    """
    A word-wrap function that preserves existing line breaks
    and most spaces in the text. Expects that existing line
    breaks are posix newlines (\n).
    """
    return reduce(lambda line, word, width=width: '%s%s%s' %
                  (line,
                   (' '+carriage_return)[(len(line[line.rfind(carriage_return)+1:])
                         + len(word.split(carriage_return,1)[0]
                              ) >= width)],
                   word),
                  text.split(' ')
                 )


def wrap_onspace_strict(text, width, carriage_return=None):
    """Similar to wrap_onspace, but enforces the width constraint:
       words longer than width are split."""
    wordRegex = re.compile(r'\S{'+str(width)+r',}')
    if carriage_return:
        return wrap_onspace(wordRegex.sub(lambda m: wrap_always(
            m.group(),width, carriage_return),text),width)
    else:
        return wrap_onspace(wordRegex.sub(lambda m: wrap_always(m.group(),width)
                                          ,text),width)


def wrap_always(text, width, carriage_return='\n'):
    """A simple word-wrap function that wraps text on exactly width characters.
       It doesn't split the text in words."""
    return carriage_return.join([text[width*i:width*(i+1)] \
                                 for i in range(int(math.ceil(1.*len(text)/width)))])

if __name__ == '__main__':
    labels = ('First Name', 'Last Name', 'Age', 'Position')
    data = \
    '''John,Smith,24,Software Engineer
       Mary,Brohowski,23,Sales Manager
       Aristidis,Papageorgopoulos,28,Senior Reseacher'''
    rows = [row.strip().split(',') for row in data.splitlines()]

    print('Without wrapping function\n')
    print(indent([labels]+rows, hasHeader=True))
    # test indent with different wrapping functions
    width = 10
    for wrapper in (wrap_always,wrap_onspace,wrap_onspace_strict):
        print('Wrapping function: %s(x,width=%d)\n' % (wrapper.__name__,width))
        print(indent([labels]+rows, hasHeader=True, separateRows=True,
                     prefix='| ', postfix=' |',
                     wrapfunc=lambda x: wrapper(x,width)))

    # output:
    #
    #Without wrapping function
    #
    #First Name | Last Name        | Age | Position
    #-------------------------------------------------------
    #John       | Smith            | 24  | Software Engineer
    #Mary       | Brohowski        | 23  | Sales Manager
    #Aristidis  | Papageorgopoulos | 28  | Senior Reseacher
    #
    #Wrapping function: wrap_always(x,width=10)
    #
    #----------------------------------------------
    #| First Name | Last Name  | Age | Position   |
    #----------------------------------------------
    #| John       | Smith      | 24  | Software E |
    #|            |            |     | ngineer    |
    #----------------------------------------------
    #| Mary       | Brohowski  | 23  | Sales Mana |
    #|            |            |     | ger        |
    #----------------------------------------------
    #| Aristidis  | Papageorgo | 28  | Senior Res |
    #|            | poulos     |     | eacher     |
    #----------------------------------------------
    #
    #Wrapping function: wrap_onspace(x,width=10)
    #
    #---------------------------------------------------
    #| First Name | Last Name        | Age | Position  |
    #---------------------------------------------------
    #| John       | Smith            | 24  | Software  |
    #|            |                  |     | Engineer  |
    #---------------------------------------------------
    #| Mary       | Brohowski        | 23  | Sales     |
    #|            |                  |     | Manager   |
    #---------------------------------------------------
    #| Aristidis  | Papageorgopoulos | 28  | Senior    |
    #|            |                  |     | Reseacher |
    #---------------------------------------------------
    #
    #Wrapping function: wrap_onspace_strict(x,width=10)
    #
    #---------------------------------------------
    #| First Name | Last Name  | Age | Position  |
    #---------------------------------------------
    #| John       | Smith      | 24  | Software  |
    #|            |            |     | Engineer  |
    #---------------------------------------------
    #| Mary       | Brohowski  | 23  | Sales     |
    #|            |            |     | Manager   |
    #---------------------------------------------
    #| Aristidis  | Papageorgo | 28  | Senior    |
    #|            | poulos     |     | Reseacher |
    #---------------------------------------------
