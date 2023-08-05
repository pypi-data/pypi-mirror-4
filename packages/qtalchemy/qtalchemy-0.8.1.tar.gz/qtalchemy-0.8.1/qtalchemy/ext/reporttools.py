# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2012, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU Lesser General Public License (LGPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import *
import decimal
import datetime

def ReportLabSize(str_pagesize):
    """
    Accepts input of a string "encoded" pagesize and translates it to a reportlab pagesize value.
    
    Example:
    >>> ReportLabSize("letter")
    (612.0, 792.0)
    >>> ReportLabSize("legal")
    (612.0, 1008.0)
    >>> # a4 page dimensions are not rounded the same on diverse platforms
    >>> tuple(AttrNumeric(2)(x) for x in ReportLabSize("landscape_a4"))
    (Decimal('841.89'), Decimal('595.28'))
    >>> ReportLabSize("landscape_letter")
    (792.0, 612.0)
    >>> ReportLabSize("portrait_letter")==ReportLabSize("letter")
    True
    """
    from reportlab.lib import pagesizes

    if str_pagesize is None:
        mod, size = "", "letter" # sorry, I'm very North American
    elif '_' in str_pagesize:
        mod, size = str_pagesize.split('_',2)
    else:
        mod, size = "", str_pagesize
    if not size.upper() in ("LETTER","LEGAL","ELEVENSEVENTEEN") + tuple("A{0}".format(i) for i in range(7)) + tuple("B{0}".format(i) for i in range(7)):
        raise ValueError( "the pagesize {0} is not valid".format(size) )
    if not mod.lower() in ("landscape","portrait",""):
        raise ValueError( "the pagesize modifier {0} is not valid".format(mod) )

    mySize = getattr(pagesizes,size.upper())
    if mod != "":
        mySize = getattr(pagesizes,mod.lower())(mySize)
    return mySize

def SuppressedZero(attr):
    def format(x):
        if x == 0:
            return ""
        else:
            return AttrNumeric(2)(x)

    return lambda instance: format(getextendedattr(instance, attr))
sz = SuppressedZero

class Numeric:
    def __init__(self, type_):
        self.type_ = type_

    def __call__(self, attr):
        def format(x):
            return str(self.type_(x))
        return lambda instance: format(getextendedattr(instance, attr))

def safe_none(v):
    """
    >>> safe_none(None)
    ''
    >>> safe_none("1234")
    '1234'
    """
    if v is None:
        v = ""
    elif isinstance(v, str):
        v = v.replace("&", "&amp;")
    return v

def u(attr):
    return lambda instance: safe_none(getextendedattr(instance, attr))

def FormattedDate(attr):
    return lambda instance: getextendedattr(instance, attr).strftime("%x")
fd = FormattedDate

def ColumnWidthRatios(cols, pageSize, marginLeft, marginRight):
    """
    Internal width computations for GeraldoElements and GeraldoHeaders.

    >>> from geraldo.utils import inch
    >>> quantize = lambda x: str(AttrNumeric(2)(x))
    >>> cols = [ModelColumn("name", str, width=15),
    ...         ModelColumn("description", str, width=35)]
    >>> ColumnWidthRatios(cols, pageSize=None, marginLeft=.5*inch, marginRight=0)
    [140.4, 327.6]
    """
    from geraldo.utils import inch
    
    if pageSize is None:
        pageSize = "LETTER" # north american bias
    pageSize = ReportLabSize(pageSize)

    detailRatios = [m.width for m in cols]
    if set(detailRatios) == set([None]):
        detailRatios = None

    # where does the 1.5 inch come from
    totalMargins = marginLeft + marginRight + 1.5*inch

    if detailRatios is None:
        detailRatios = [(pageSize[0] - totalMargins) / len(cols)] * len(cols)
    else:
        widths = sum(detailRatios)
        for i in range(len(cols)):
            detailRatios[i] = detailRatios[i] * (pageSize[0] - totalMargins) / widths

    return detailRatios

def GeraldoElements(cols, pageSize=None, marginLeft=0, marginRight=0):
    """
    Return a list of geraldo elements converted from a list of ModelColumn objects.
    
    :param cols:  list of ModelColumn objects
    :param pageSize:  a string page size name.  See :func:`ReportLabSize`
    :param marginLeft:  padding for empty space to the left
    :param marginRight:  padding for empty space to the right
    
    >>> from geraldo.utils import cm, inch
    >>> quantize = lambda x: str(AttrNumeric(2)(x))
    >>> cols = [ModelColumn("name", str, width=15),
    ...         ModelColumn("description", str, width=35)]
    >>> elts = GeraldoElements(cols)
    >>> [quantize(o.width) for o in elts]
    ['151.20', '352.80']
    >>> [quantize(o.left) for o in elts]
    ['0.00', '151.20']
    
    >>> elts = GeraldoElements(cols, marginLeft=2*cm)
    >>> [quantize(o.width) for o in elts]
    ['134.19', '313.12']
    >>> [quantize(o.left) for o in elts]
    ['56.69', '190.89']
    """
    from geraldo import ObjectValue, SystemField
    from geraldo.utils import inch
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    detailRatios = ColumnWidthRatios(cols, pageSize, marginLeft, marginRight)

    det_elements = []
    for i in range(len(cols)):
        wf = u
        style = {}
        padRight = 0
        if cols[i].type_ is decimal.Decimal:
            style['alignment'] = TA_RIGHT
            #wf = sz
            padRight = .1*inch
        elif isinstance(cols[i].type_, AttrNumeric):
            style['alignment'] = TA_RIGHT
            wf = Numeric(cols[i].type_)
            padRight = .1*inch
        elif cols[i].type_ is datetime.date:
            wf = fd
        else:
            style['wordWrap'] = True
        
        det_elements.append(ObjectValue(
                    attribute_name=cols[i].attr, 
                    get_value=wf(cols[i].attr), 
                    top=0, 
                    left=marginLeft + sum([detailRatios[j] for j in range(i)]), 
                    width=detailRatios[i] - padRight, 
                    style=style))

    return det_elements


def GeraldoHeaders(cols, pageSize=None, marginLeft=0, marginRight=0):
    """
    Return a list of geraldo elements converted from a list of ModelColumn objects.
    
    :param cols:  list of ModelColumn objects
    :param pageSize:  a string page size name.  See :func:`ReportLabSize`
    :param marginLeft:  padding for empty space to the left
    :param marginRight:  padding for empty space to the right
    
    >>> from geraldo.utils import cm, inch
    >>> quantize = lambda x: str(AttrNumeric(2)(x))
    >>> cols = [ModelColumn("name", str, width=15),
    ...         ModelColumn("description", str, width=35)]
    >>> elts = GeraldoHeaders(cols)
    >>> [quantize(o.width) for o in elts]
    ['151.20', '352.80']
    >>> [quantize(o.left) for o in elts]
    ['0.00', '151.20']
    
    >>> elts = GeraldoHeaders(cols, marginLeft=2*cm)
    >>> [quantize(o.width) for o in elts]
    ['134.19', '313.12']
    >>> [quantize(o.left) for o in elts]
    ['56.69', '190.89']
    """
    from geraldo import ObjectValue, SystemField

    detailRatios = ColumnWidthRatios(cols, pageSize, marginLeft, marginRight)

    det_elements = []
    for i in range(len(cols)):
        det_elements.append(SystemField(
                    expression=cols[i].label,
                    top=0, 
                    left=marginLeft + sum([detailRatios[j] for j in range(i)]), 
                    width=detailRatios[i]))

    return det_elements

