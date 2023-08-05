from datetime import datetime
from datetime import timedelta

def delta2dict( delta ):
    """return dictionary of delta"""
    delta = abs( delta )
    return { 
        'year'   : delta.days / 365 ,
        'day'    : delta.days % 365 ,
        'hour'   : delta.seconds / 3600 ,
        'minute' : (delta.seconds / 60) % 60 ,
        'second' : delta.seconds % 60 ,
        'microsecond' : delta.microseconds
    }

def delta2human(delta, precision=2, past_format='{0} ago', future_format='in {0}'):
    """return human readable delta string"""
    the_format = past_format
    if delta < timedelta(0): the_format = future_format
    d = delta2dict( delta )
    hlist = [] 
    count = 0
    units = ( 'year', 'day', 'hour', 'minute', 'second', 'microsecond' )
    for unit in units:
        if count >= precision: break # met precision
        if d[ unit ] == 0: continue # skip 0's
        s = '' if d[ unit ] == 1 else 's' # handle plurals
        hlist.append( '%s %s%s' % ( d[unit], unit, s ) )
        count += 1
    human_delta = ', '.join( hlist )
    return the_format.format(human_delta) 

def human(d, precision=2, format_past='{0} ago', format_future='in {0}'):
    """Pass datetime we will return human delta string"""
    delta = datetime.now() - d
    return delta2human( delta, precision, format_past, format_future ) 

if __name__ == "__main__": 
    from test_ago import test_output
    test_output()
