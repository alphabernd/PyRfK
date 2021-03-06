#!/usr/bin/env python

import os
import sys
import struct
import time
import urllib2

import rfk
import rfk.database
from rfk.database import init_db
from rfk.database.streaming import Relay
from rfk.database.stats import RelayStatistic
from rfk.icecast import Icecast
from rfk.helper import now, get_path

rfk.init()
init_db("%s://%s:%s@%s/%s" % (rfk.CONFIG.get('database', 'engine'),
                              rfk.CONFIG.get('database', 'username'),
                              rfk.CONFIG.get('database', 'password'),
                              rfk.CONFIG.get('database', 'host'),
                              rfk.CONFIG.get('database', 'database')))

def get_stats(relay):
    statsfile = get_path(os.path.join('var', 'tmp', 'traffic{0}'.format(relay.relay)))
    try:
        with open(statsfile) as f:
            (last_total, last_timestamp) = struct.unpack('qi', f.read())
    except IOError, struct.error:
        last_total = None
        last_timestamp = None
    ic = Icecast(relay.address, relay.port, relay.admin_username, relay.admin_password)
    total = ic.get_traffic(True)
    timestamp = int(time.time())
    
    with open(statsfile,'wb') as f:
        f.write(struct.pack('qi', total, timestamp))
    if last_total is not None:
        return ((total-last_total)/(timestamp-last_timestamp))/1024
    

def main():
    for relay in Relay.query.all():
        try:
            relay.usage = get_stats(relay)
            rs = RelayStatistic.get_relaystatistic(relay, RelayStatistic.TYPE.TRAFFIC)
            if relay.usage is not None:
                rs.statistic.set(now(),relay.usage)
            rfk.database.session.commit()
        except urllib2.URLError:
            pass
        
if __name__ == '__main__':
    sys.exit(main())


