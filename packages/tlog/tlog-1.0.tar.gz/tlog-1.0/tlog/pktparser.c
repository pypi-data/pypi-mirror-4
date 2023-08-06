#include <Python.h>
#include "structmember.h"
#include <arpa/inet.h>

struct ethernet_header {
  unsigned char dst[6];
  unsigned char src[6];
  u_int16_t type;
};


struct ip_header {
  //!!LITTLE ENDIAN ASSUMED!!
  unsigned char ihl:4,
    version:4;
  unsigned char tos;
  unsigned short length, id, fragment_offset;
  unsigned char ttl, protocol;
  unsigned short check;
  unsigned int src, dst;  
};

struct tcp_header {
  unsigned short src, dst;
  unsigned int seq, ack_seq;
  unsigned char res;
  unsigned char flags;
  unsigned short window;
  unsigned int checksum, options;
};

struct udp_header {
  unsigned short src, dst,len,checksum;
};

#define ETH_LEN 14
#define IP_LEN 20
#define TCP_LEN (sizeof(struct tcp_header))
#define UDP_LEN (sizeof(struct udp_header))


typedef struct {
  PyObject_HEAD
  unsigned char src_mac[7], dst_mac[7];
  unsigned int customer_ip, src_ip, dst_ip, eth_type;
  char vpn, icmp, tcp, udp, ip, valid, syn, fin, ack;
  int direction;
  unsigned short src_port, dst_port, flags, ip_length;
  u_int16_t ipproto;
  unsigned short tx, rx;
  PyObject * log_entry;
} pktparser_Packet;

static PyObject *
PacketType_init(pktparser_Packet * self, PyObject * args, PyObject *kwds) {
  const char * raw;
  int raw_lgt, gwlen;
  const unsigned char * gateway_mac;
  double t1;

  static char * kwlist[] = {"raw", "gateway_mac", "t1", NULL};
  if (! PyArg_ParseTupleAndKeywords(args, kwds, "s#s#d", kwlist, 
				    &raw, &raw_lgt, &gateway_mac, &gwlen, &t1 )) {
    return -1;
  }
  
  self->tcp = self->udp = self->valid = self->ip = 0;
  self->customer_ip = self->tx = self->rx = self->direction = 0;
  self->log_entry = NULL;

  if (raw_lgt < ETH_LEN) self->valid = 0;
  else {
    struct ethernet_header * eth = (struct ethernet_header *) raw;  
    memcpy ( self->src_mac, eth->src, 6); self->src_mac[6] = 0;
    memcpy ( self->dst_mac, eth->dst, 6); self->dst_mac[6] = 0;
    self->valid = -1;
    self->ip = (self->eth_type = ntohs ( eth->type )) == 0x800;
    
    if ( memcmp((const char *)gateway_mac, (const char *)self->src_mac, 6) == 0 ) self->direction = 2;
    if ( memcmp((const char *)gateway_mac, (const char *)self->dst_mac, 6) == 0 ) self->direction = 1;

    if (self->ip) {
      struct ip_header * ip = (struct ip_header *) (raw + sizeof(struct ethernet_header));

      self->src_ip = ip->src;
      self->dst_ip = ip->dst;
      self->ip_length = ntohs(ip->length);
      
      if (self->direction == 1) { self->tx = self->ip_length; self->customer_ip = self->src_ip; }
      else if (self->direction == 2) { self->rx = self->ip_length; self->customer_ip = self->dst_ip; }

      self->ipproto = ip->protocol;
      self->tcp = (ip->protocol == 6);
      self->udp = (ip->protocol == 17);
      self->icmp = (ip->protocol == 1);
      self->vpn = (ip->protocol == 47) || (ip->protocol == 50) || (ip->protocol == 51);
      if (self->tcp) {
	struct tcp_header * tcp = (struct tcp_header *) (raw + ETH_LEN + ip->ihl * 4);
	self->src_port = ntohs(tcp->src);
	self->dst_port = ntohs(tcp->dst);
	self->flags = tcp->flags;
	self->fin = self->flags & 1;
	self->syn = self->flags & 2;
	self->ack = self->flags & 16;
	if (self->syn && self->ack) { 
	  self->log_entry = Py_BuildValue ( "(dIHIHH)", t1, self->dst_ip, self->dst_port, self->src_ip, self->src_port, 1 );
	} else if (self->fin) {
	  self->log_entry = Py_BuildValue ( "(dIHIHH)", t1, self->src_ip, self->src_port, self->dst_ip, self->dst_port, 0 );
	}
      } else if (self->udp) {
	struct udp_header * udp = (struct udp_header *) (raw + ETH_LEN + ip->ihl * 4);
	self->src_port = ntohs(udp->src);
	self->dst_port = ntohs(udp->dst);
      } 
    }
    
    //self->src_mac[6] = 0;
  }

  return 0;
}

static void
PacketType_dealloc(pktparser_Packet* self)
{
  if (self->log_entry) {
    Py_XDECREF(self->log_entry);
  }
  self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
PacketType_str(pktparser_Packet * self) {
  char src_mac[18], dst_mac[18];
  char src_ip[16], dst_ip[16];
  char l3[256], l4[1024];
  l3[0] = 0;
  l4[0] = 0;
  if (!self->valid) 
    return PyString_FromFormat ( "invalid packet" );
  
  snprintf ( src_mac, 18, "%02x:%02x:%02x:%02x:%02x:%02x", 
	     self->src_mac[0], self->src_mac[1],self->src_mac[2],
	     self->src_mac[3],self->src_mac[4],self->src_mac[5] );
  snprintf ( dst_mac, 18, "%02x:%02x:%02x:%02x:%02x:%02x", 
	     self->dst_mac[0], self->dst_mac[1],self->dst_mac[2],
	     self->dst_mac[3],self->dst_mac[4],self->dst_mac[5] );
  
  if (self->ip) {
    struct in_addr src, dst;
    src.s_addr = self->src_ip;
    dst.s_addr = self->dst_ip;
    snprintf ( src_ip, sizeof(src_ip), "%s", inet_ntoa ( src ) );
    snprintf ( dst_ip, sizeof(dst_ip), "%s", inet_ntoa ( dst ) );
    snprintf ( l3, sizeof(l3), "IP %s > %s (%db) %s%s%s%s", 
	       src_ip, dst_ip, self->ip_length,
	       (self->tcp ? "TCP" : ""), 
	       (self->udp ? "UDP" : ""), 
	       (self->icmp ? "ICMP" : ""), 
	       (self->vpn ? "VPN" : "") );	   
    if (self->tcp) {
      snprintf ( l4, sizeof(l4), " %d > %d %s%s%s", self->src_port, self->dst_port,
		 (self->syn ? "Syn" : ""), (self->ack ? "Ack" : ""), (self->fin ? "Fin" : "") );
    } else if (self->udp) {
      snprintf ( l4, sizeof(l4), " %d > %d", self->src_port, self->dst_port );
    }
  
  }

  return PyString_FromFormat ( "(%s%s)%s%s", self->direction == 2? "D" : "", self->direction==1 ? "U" : "", l3, l4 );
}

static PyMemberDef PacketType_members[] = {
{"src_mac", T_STRING_INPLACE, offsetof(pktparser_Packet, src_mac), READONLY, "source MAC"},
{"dst_mac", T_STRING_INPLACE, offsetof(pktparser_Packet, dst_mac), READONLY, "destination MAC"},
{"tcp", T_BOOL, offsetof(pktparser_Packet, tcp), 0, "is it a TCP packet?"},
{"udp", T_BOOL, offsetof(pktparser_Packet, udp), 0, "is it a UDP packet?"},
{"ip", T_BOOL, offsetof(pktparser_Packet, ip), 0, "is it an IP packet?"},
{"icmp", T_BOOL, offsetof(pktparser_Packet, icmp), 0, "is it an ICMP packet?"},
{"vpn", T_BOOL, offsetof(pktparser_Packet, vpn), 0, "is it a VPN packet?"},
{"valid", T_BOOL, offsetof(pktparser_Packet, valid), 0, "is it a valid packet?"},
{"eth_type", T_UINT, offsetof(pktparser_Packet, eth_type), 0, "ethernet type"},
{"direction", T_INT, offsetof(pktparser_Packet, direction), 0, ""},
{"rx", T_USHORT, offsetof(pktparser_Packet, rx), 0, ""},
{"tx", T_USHORT, offsetof(pktparser_Packet, tx), 0, ""},
{"syn", T_BOOL, offsetof(pktparser_Packet, syn), 0, ""},
{"fin", T_BOOL, offsetof(pktparser_Packet, fin), 0, ""},
{"ack", T_BOOL, offsetof(pktparser_Packet, ack), 0, ""},
{"src_ip", T_UINT, offsetof(pktparser_Packet, src_ip), 0, ""},
{"dst_ip", T_UINT, offsetof(pktparser_Packet, dst_ip), 0, ""},
{"customer_ip", T_UINT, offsetof(pktparser_Packet, customer_ip), 0, ""},
{"ip_length", T_USHORT, offsetof(pktparser_Packet, ip_length), 0, ""},
{"src_port", T_USHORT, offsetof(pktparser_Packet, src_port), 0, ""},
{"dst_port", T_USHORT, offsetof(pktparser_Packet, dst_port), 0, ""},
{"ip_protocol", T_USHORT, offsetof(pktparser_Packet, ipproto), 0, ""},
{"log_entry", T_OBJECT, offsetof(pktparser_Packet, log_entry), 0, ""},
{NULL}  
};


static PyMethodDef PacketType_methods[] = {
  //  {"name", (PyCFunction)Noddy_name, METH_NOARGS,
  //  "Return the name, combining the first and last name"
  //},
  {NULL}  /* Sentinel */
};

static PyTypeObject pktparser_PacketType = {
  PyObject_HEAD_INIT(NULL)
  0,                         /*ob_size*/
  "pktparser.Packet",        /*tp_name*/
  sizeof(pktparser_Packet),  /*tp_basicsize*/
  0,                         /*tp_itemsize*/
  PacketType_dealloc,        /*tp_dealloc*/
  0,                         /*tp_print*/
  0,                         /*tp_getattr*/
  0,                         /*tp_setattr*/
  0,                         /*tp_compare*/
  0,                         /*tp_repr*/
  0,                         /*tp_as_number*/
  0,                         /*tp_as_sequence*/
  0,                         /*tp_as_mapping*/
  0,                         /*tp_hash */
  0,                         /*tp_call*/
  (reprfunc)PacketType_str,                         /*tp_str*/
  0,                         /*tp_getattro*/
  0,                         /*tp_setattro*/
  0,                         /*tp_as_buffer*/
  Py_TPFLAGS_DEFAULT,        /*tp_flags*/
  "Parsed packets",          /* tp_doc */
  0,               /* tp_traverse */
  0,               /* tp_clear */
  0,               /* tp_richcompare */
  0,               /* tp_weaklistoffset */
  0,               /* tp_iter */
  0,               /* tp_iternext */
  PacketType_methods,             /* tp_methods */
  PacketType_members,             /* tp_members */
  0,                         /* tp_getset */
  0,                         /* tp_base */
  0,                         /* tp_dict */
  0,                         /* tp_descr_get */
  0,                         /* tp_descr_set */
  0,                         /* tp_dictoffset */
  (initproc)PacketType_init,      /* tp_init */
  0,                         /* tp_alloc */
  0,                         /* tp_new */
};


static PyObject *
parse (PyObject * self, PyObject * args) {
  const char * raw;
  int length;
  
  if (!PyArg_ParseTuple(args, "s#", &raw, &length))
    return NULL;
  
  PyObject * P = Py_None;

  if (length >= ETH_LEN) {
    struct ethernet_header * eth = (struct ethernet_header *) raw;
    P = Py_BuildValue ( "{ss#ss#sH}", "dst", eth->dst, 6, "src", eth->src, 6, "type", ntohs(eth->type) );

    switch ntohs(eth->type) {
      case 0x0800: 
	if (length >= (ETH_LEN + IP_LEN))
        {	  
	  struct ip_header * ip = (struct ip_header *) (raw + sizeof(struct ethernet_header));
	  PyObject * ip_fields = Py_BuildValue ( "{sbsHsIsI}", "protocol", ip->protocol, "length", ntohs(ip->length), 
					       "src", ip->src, "dst", ip->dst );
	  PyObject * payload = NULL;
	  PyDict_SetItemString (P, "ip", ip_fields );
	  Py_DECREF (ip_fields);
	  
	  switch (ip->protocol) {
	  case 6: //tcp
	      {
		struct tcp_header * tcp = (struct tcp_header *) (raw + ETH_LEN + ip->ihl * 4);
		PyObject * _tcp = Py_BuildValue ( "{sHsHsb}", "src", ntohs(tcp->src), "dst", ntohs(tcp->dst), "flags", tcp->flags );
		payload = Py_BuildValue ( "s#", (raw + ETH_LEN + ip->ihl*4 + TCP_LEN), length - ETH_LEN - ip->ihl*4 - TCP_LEN );
		PyDict_SetItemString(P, "tcp", _tcp );
		Py_DECREF(_tcp);
	      }
	      break;
	    case 17:
	      {
		struct udp_header * udp = (struct udp_header *) (raw + ETH_LEN + ip->ihl * 4);
		PyObject * _udp = Py_BuildValue ( "{sHsH}", "src", ntohs(udp->src), "dst", ntohs(udp->dst) );
		payload = Py_BuildValue ( "s#", (raw + ETH_LEN + ip->ihl*4 + UDP_LEN), length - ETH_LEN - ip->ihl*4 - UDP_LEN );
		PyDict_SetItemString(P, "udp", _udp );		
		Py_DECREF(_udp);
	      }
	      break;
	    case 1:
              {
		PyDict_SetItemString(P, "icmp", Py_True );		
	      }
	      break;
  	    case 47:
	    case 50:
	    case 51:
	      {
		PyDict_SetItemString(P, "vpn", Py_True );
	      }
	      break;
	  };
	  if (payload) {
	    PyDict_SetItemString (P, "payload", payload );
	    Py_DECREF(payload);
	  }
        }
	break;
      default:
	break;
    }
  }
  
  return P;
}

PyMethodDef methods[] = {
  {"parse", parse, METH_VARARGS, "Parse a captured ethernet packet."},
  {NULL, NULL, 0, NULL}
};

PyMODINIT_FUNC 
initpktparser() {
  PyObject *module;

  pktparser_PacketType.tp_new = PyType_GenericNew;
  if (PyType_Ready(&pktparser_PacketType) < 0)
    return;
  
  module = Py_InitModule3("pktparser", methods, "Fast packet parsing.");
  Py_INCREF (&pktparser_PacketType);
  PyModule_AddObject ( module, "Packet", (PyObject *) &pktparser_PacketType );
}

