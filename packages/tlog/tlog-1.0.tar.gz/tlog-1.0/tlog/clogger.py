import os, os.path, time, zlib, copy, socket, re, sqlite3
from pyrrd.rrd import RRD, RRA, DS
from multiprocessing import Process
from struct import pack, unpack, Struct
from tools import *
from sniffer import Sniffer
import syslog

import sys


        
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
        from tlog import pktparser
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

            p = pktparser.Packet (self.sniffer.next(), self.router_mac, t1)

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
                

            if not p.ip: continue

            if p.tx > 0:
                stats.tx_bytes.add ( p.customer_ip, p.tx )
                stats.tx_packets.add ( p.customer_ip, 1 )
                stats.ttx_bytes += p.tx
                stats.ttx_pps += 1
            elif p.rx > 0:
                stats.rx_bytes.add ( p.customer_ip, p.rx )
                stats.rx_packets.add ( p.customer_ip, 1 )
                stats.trx_bytes += p.rx
                stats.trx_pps += 1

            stats.activity._or (p.customer_ip, p.direction)
            
            if p.log_entry:
                stats.add_log_entry ( *p.log_entry )

            if p.tcp:
                if p.syn and p.direction == 1:  #connection opened by customer
                    if p.dst_port == 25:
                        stats.used_smtp.add_to_set(p.src_ip, p.dst_ip)
                    elif p.dst_port in [143,993,110,995]:
                        stats.used_mailserver.add_to_set(p.src_ip, p.dst_ip)                    
                elif p.syn and p.direction == 2:  #connection opened to customer
                    if p.dst_port in [25,465]:
                        stats.ip_opts[p.dst_ip].is_smtpd = True
                    elif p.dst_port in [80,443]:
                        stats.ip_opts[p.dst_ip].is_httpd = True
                pass
            elif p.udp: 
                if p.dst_port == 53:
                    if p.direction == 1:
                        stats.used_dns.add_to_set(p.src_ip, p.dst_ip)
                    elif p.direction == 2:
                        stats.ip_opts[p.dst_ip].is_dns = True
            elif p.vpn:  
                stats.ip_opts[p.customer_ip].used_vpn = True

                                                           
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
    

if __name__ == "__main__":    
    Logger ( "/tmp", interface="eth2",
                router_mac="00:69:71:8a:f0:f8",
                log_interval=120,
                rrd_nets = [ "83.243.32.0", "77.95.48.0"], daemon=False )
