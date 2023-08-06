import sqlite3, zlib, struct, time

import socket

def ipstr(i):
    return socket.inet_ntoa ( struct.pack ( 'I', i ) )

def dumplog(files):
    S = struct.Struct ( 'BLIHIHB' )
    for file in files:        
        db = sqlite3.connect (file)
        cur = db.cursor()
        cur.execute ( "SELECT t1,t2,entries FROM log ORDER BY t1 ASC" )
        for r in cur:
            t1,t2,entries = r
            entries = zlib.decompress (entries)
            for s in xrange(0,len(entries),S.size):
                _,t,src_ip,src_port,dst_ip,dst_port,action = S.unpack ( entries[s:s+S.size] )
                if action == 1: act = "CONNECT"
                elif action == 0: act = "CLOSE" 
                print "{0} ({1:7}) {4}:{5} >> {2}:{3}".format( time.strftime("%Y-%m-%d %H:%M:%S",  time.localtime(t)),
                                                          act, ipstr(src_ip),src_port, ipstr(dst_ip), dst_port )
            
        cur.close()
        db.close()
        

if __name__ == "__main__":
    import sys
    dumplog ( sys.argv[1:] )
