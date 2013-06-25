import pytz
import datetime
import rfk
from flaskext.babel import lazy_gettext
from flask import url_for

def now():
    return pytz.utc.localize(datetime.datetime.utcnow())

def get_location(address):
    return rfk.geoip.record_by_addr(address)

def natural_join(lst):
    l = len(lst);
    if l <= 2:
        return lazy_gettext(' and ').join(lst)
    elif l > 2:
        first =  ', '.join(lst[0:-1])
        return "%s %s %s" % (first, lazy_gettext('and'), lst[-1])
    
def make_user_link(user):
    return '<a href="%s" title="%s">%s</a>' % (url_for('user.info',user=user.username),user.username,user.username);