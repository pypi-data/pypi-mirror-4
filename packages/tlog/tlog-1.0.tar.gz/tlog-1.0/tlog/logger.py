import os, os.path, time, zlib, copy, socket, re, sqlite3
from pyrrd.rrd import RRD, RRA, DS
from multiprocessing import Process
from struct import pack, unpack, Struct
from tools import *
from sniffer import Sniffer
import syslog
        
class stats_container(object):
    
    def __init__(self):
        self.rx_bytes = sum_dict(0)
        self.tx_bytes = sum_dict(0)
        self.rx_packets = sum_dict(0)
        self.tx_packets = sum_dict(0)
        self.used_dns = sum_dict(0)
        self.total = sum_dict(0)
        self.trx_pps, self.ttx_pps, self.trx_bytes, self.ttx_bytes = 0,0,0,0
        self.activity = sum_dict(0)
        self.used_smtp = sum_dict(0)
        self.used_mailserver = sum_dict(0)
        self.ip_opts = rec_dict()
        self.log_struct = Struct ( 'BLIHIHB' )
        self.log = []

    def add_log_entry (self, ts, ip1, p1, ip2, p2, act ):
        entry = self.log_struct.pack ( self.log_struct.size, long(ts), ip1, p1, ip2, p2, act )
        self.log.append (entry)
        
    def flush_log(self):
        snapshot = copy.copy(self.log)
        self.log = []
        return snapshot

    @staticmethod
    def snapshot(stats_instance):
        pass

def check_in_nets(ip, nets):
    for n in nets:
        if n & ip == n: return True
    return False

    
class Logger(object):
        
    def __init__(self, data_dir,
                 interface="eth0", router_mac="00:00:00:00:00:00", log_interval=120,
                 stat_dump_interval=300, rrd_nets=[], daemon=False):

        self.data_dir = data_dir
        self.log_dir = os.path.join ( self.data_dir, "traffic" )
        self.rrd_dir = os.path.join ( self.data_dir, "rrd" )
        self.rrd_global_dir = os.path.join ( self.rrd_dir, "global" )
        self.rrd_customer_dir = os.path.join ( self.rrd_dir, "customer" )
        for p in [self.data_dir, self.log_dir, self.rrd_dir, self.rrd_customer_dir, self.rrd_global_dir]:
            if not os.path.exists(p):
                os.makedirs (p)

        self.log_interval = log_interval
        self.stat_dump_interval = stat_dump_interval

        self.router_mac = "".join( map( lambda c: chr(int(c, 16)), router_mac.split(":")) )
        self.interface = interface
        
        customer_ds = []
        customer_ds.append ( DS (dsName = 'rx_octets', dsType='COUNTER', heartbeat=120, minval=0) )
        customer_ds.append ( DS (dsName = 'tx_octets', dsType='COUNTER', heartbeat=120, minval=0) )
        customer_ds.append ( DS (dsName = 'rx_packets', dsType='COUNTER', heartbeat=120, minval=0) )
        customer_ds.append ( DS (dsName = 'tx_packets', dsType='COUNTER', heartbeat=120, minval=0) )
        self.customer_ds = customer_ds

        self.active_hosts_ds = [ DS (dsName = 'active_hosts', dsType='GAUGE', heartbeat=120, minval=0) ]
        self.active_hosts_rra = [ RRA(cf='AVERAGE', xff=0, steps=1, rows=30*24*365*3) ]
        
        customer_rra = []
        customer_rra.append ( RRA(cf='AVERAGE', xff=0, steps=1, rows=30*24) )
        customer_rra.append ( RRA(cf='MAX', xff=0, steps=5, rows=6*24*7) )
        customer_rra.append ( RRA(cf='MAX', xff=0, steps=30, rows=24*30) )
        self.customer_rrd_step = 120
        self.customer_rra = customer_rra

        self.rrd_nets = map ( lambda n: unpack('I', socket.inet_aton(n))[0], rrd_nets )


        if daemon:
            from daemonize import daemonize
            daemonize ()
            
        self.sniffer_process()
        
    def sniffer_process(self):
        import pktparser
        syslog.openlog ( 'traffic', 0, syslog.LOG_USER )
        syslog.syslog ( "START!" )
        self.sniffer = Sniffer(self.interface)
        stats = stats_container()
        t0 = time.time()
        log_t2 = t0
        last_log_write_time = 0
        writer = Process (target=self.log_writer_process, args=(0,0,None,None))
        writer.start()
        
        while True:
            t1 = time.time()
            t1_s = long(t1)

            if t1 - t0 > 10 and t1_s != last_log_write_time and t1_s % self.log_interval == 0:
                last_log_write_time = t1_s            
                dump_start_time = time.time()

                logs = stats.flush_log()

                if writer.is_alive: writer.terminate()
                writer.join()

                wstats = copy.copy(stats)
                writer = Process ( target = self.log_writer_process,
                                   args = (log_t2, t1, "".join(logs), wstats) )
                writer.start()

                dt = time.time() - log_t2

                syslog.syslog ("current traffic: pps>  rx: {0}, tx:{1} ".format ( stats.trx_pps / dt, stats.ttx_pps / dt ) )
                syslog.syslog ("current traffic: Mbps> rx: {0}, tx:{1} ".format (
                    stats.trx_bytes / dt / 1000 / 1000 * 8,
                    stats.ttx_bytes / dt / 1000 / 1000 * 8 ) )
                syslog.syslog ("Active hosts: {0}".format( len(stats.activity) ) )

                stats.trx_pps, stats.ttx_pps, stats.trx_bytes, stats.ttx_bytes = 0,0,0,0
                stats.activity.clear()
                
                log_t2 = t1
                

            p = pktparser.parse (self.sniffer.next())

            if "ip" not in p: continue
            
            direction = 0
            l2, l3 = p, p["ip"]
            if "tcp" in p: l4 = p["tcp"] 
            elif "udp" in p: l4 = p["udp"]
            else: l4 = { "tlog" : 0, "dst" : 0 }
            src3,dst3,src4,dst4 = l3["tlog"], l3["dst"], l4["tlog"], l4["dst"]
            lgt = l3["length"]
            
            if l2['dst'] == self.router_mac:
                stats.tx_bytes.add ( src3, lgt )
                stats.tx_packets.add ( src3, 1)
                stats.ttx_pps += 1
                stats.ttx_bytes += lgt
                direction = 1
                customer_ip = src3
            elif l2['tlog'] == self.router_mac:
                stats.rx_bytes.add ( dst3, lgt )
                stats.rx_packets.add ( dst3, 1 )
                stats.trx_pps += 1
                stats.trx_bytes += lgt
                direction = 2
                customer_ip = dst3
            else: #TODO: broadcast?
                continue
            stats.activity._or (customer_ip, direction)
            
            if "tcp" in p:
                flags = l4['flags']
                fin = flags & 1
                syn = flags & 2
                ack = flags & 16
                if syn and ack:   #connection established 
                    stats.add_log_entry(  t1, dst3, dst4, src3, src4, 1 )
                    pass
                elif fin:              #connection finished  
                    stats.add_log_entry ( t1, src3, src4, dst3, dst4, 0 ) 
                    pass
                elif syn and direction == 1:  #connection opened by customer
                    if dst4 == 25:
                        stats.used_smtp.add_to_set(src3, dst3)
                    elif dst4 in [143,993,110,995]:
                        stats.used_mailserver.add_to_set(src3, dst3)                    
                elif syn and direction == 2:  #connection opened to customer
                    if dst4 in [25,465]:
                        stats.ip_opts[dst3].is_smtpd = True
                    elif dst4 in [80,443]:
                        stats.ip_opts[dst3].is_httpd = True
                pass
            elif 'udp' in p: 
                if dst4 == 53:
                    if direction == 1:
                        stats.used_dns.add_to_set(src3, dst3)
                    elif direction == 2:
                        stats.ip_opts[dst3].is_dns = True
                elif 'vpn' in p:  
                    stats.ip_opts[customer_ip].used_vpn = True
                pass
                                                           
    def log_writer_process(self, t1, t2, blob, stats):
        if blob is None:
            return
        time.sleep(1)

        write_start = time.time()
        current_dir = os.path.join (self.log_dir, time.strftime("%Y-%m/%d", time.localtime(t1)) )
        if not os.path.exists(current_dir):
            os.makedirs ( current_dir )
        current_database_file = os.path.join(current_dir, time.strftime("log-%H.sql", time.localtime(t1)))


        if not os.path.exists ( current_database_file ):
            db = sqlite3.connect ( current_database_file )
            db.execute ( "CREATE TABLE log(t1,t2,entries);" )
            db.commit()
        else:
            db = sqlite3.connect ( current_database_file )    

        zblob = zlib.compress ( blob, 3 )
        cur = db.cursor()
        cur.execute ( "INSERT INTO log VALUES (?,?,?)", (t1, t2, sqlite3.Binary(zblob)) )
        db.commit()
        db.close()

        syslog.syslog ("Compressed Log: {0}% {1} bytes.".format ( 100 * len(zblob) / len(blob), len(zblob) ) )

        rrd_count = 0
        for _ip in stats.tx_bytes:            
            ip = ipstr(_ip)

            if not check_in_nets (_ip, self.rrd_nets): continue
            if stats.activity.get(_ip, 0) != 3: continue
            
            filename = os.path.join ( self.rrd_customer_dir, ip + '.rrd' )
            if not os.path.isfile(filename):
                myRRD = RRD (filename,
                             step=self.customer_rrd_step,
                             ds=self.customer_ds,
                             rra=self.customer_rra, start=int(t1))
                myRRD.create()
            else:
                myRRD = RRD (filename)
                myRRD.bufferValue ( int( (t2 + t1) / 2 ),
                                    stats.rx_bytes.get(_ip,0),
                                    stats.tx_bytes.get(_ip,0),
                                    stats.rx_packets.get(_ip,0),
                                    stats.tx_packets.get(_ip,0) )
            myRRD.update()
            rrd_count += 1

        filename = os.path.join ( self.rrd_global_dir, 'active.rrd' )

        if not os.path.isfile(filename):
            myRRD = RRD (filename,
                         step=self.customer_rrd_step,
                         ds=self.active_hosts_ds,
                         rra=self.active_hosts_rra, start=int(t1))
            myRRD.create()
        else:
            myRRD = RRD (filename)
            myRRD.bufferValue ( int( (t2 + t1) / 2 ), rrd_count )
        myRRD.update()
        
        syslog.syslog ("Writing in {0}s. Wrote {1} RRDs.".format( time.time() - write_start, rrd_count ) )


    def stats_dumper_process(self):
        pass
    

