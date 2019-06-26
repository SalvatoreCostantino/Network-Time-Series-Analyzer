from bcc import BPF
import time
import sys
from socket import inet_pton, AF_INET, inet_ntoa, AF_INET6, inet_ntop
from struct import pack, unpack
import multiprocessing

blockIpv4=None
blockIpv6=None
blockMac=None
device=None

# XDP_FLAGS_SKB_MODE
flags = 0|2 << 0
mode = BPF.XDP
ret = "XDP_DROP"
ctxtype = "xdp_md"

# load BPF program
b = BPF(text = """
#define KBUILD_MODNAME "foo"
#include <uapi/linux/bpf.h>
#include <linux/in.h>
#include <linux/if_ether.h>
#include <linux/if_packet.h>
#include <linux/if_vlan.h>
#include <linux/ip.h>
#include <linux/ipv6.h>

//tabella hash per bloccare IP (key: IP address, value: counter)
BPF_TABLE("percpu_hash", uint32_t, uint64_t, ipv4Blacklist, 10000);
BPF_TABLE("percpu_hash", uint64_t, uint64_t, macBlacklist, 10000);
BPF_TABLE("percpu_hash", unsigned __int128, uint64_t, ipv6Blacklist, 10000);


static inline unsigned __int128 ipv62u128(__be32* addr){
    unsigned __int128 ipv6;
    ipv6 = (unsigned __int128)(*addr);
    return ipv6;
}

static inline int parse_ipv6_ip(void*data, u64 nh_off, void *data_end, unsigned __int128* ipv6Eg, unsigned __int128* ipv6In) {
    struct ipv6hdr *ipv6h = data + nh_off;
    //se ho l'header ipv6
    if ((void*)&ipv6h[1] > data_end){
        return 0;
    }

    *ipv6In = ipv62u128((ipv6h->saddr).s6_addr32);
    *ipv6Eg = ipv62u128((ipv6h->daddr).s6_addr32);
    return 1;
}

static inline int parse_ipv4_ip(void*data, u64 nh_off, void *data_end, uint32_t* ipEg, uint32_t* ipIn) {
    struct iphdr *iph = data + nh_off;
    //se ho l'header ipv4
    if ((void*)&iph[1] > data_end){
        return 0;
    }
    *ipIn = iph->saddr;
    *ipEg = iph->daddr;
    return 1;
}

static inline uint64_t mac2u64(unsigned char* mac) {
    uint64_t macVal;
    macVal =    (uint64_t)mac[0] << 40  | 
                (uint64_t)mac[1] << 32  | 
                (uint64_t)mac[2] << 24  | 
                (uint64_t)mac[3] << 16  | 
                (uint64_t)mac[4] << 8   |
                (uint64_t)mac[5];
    
    return macVal;
}

static inline int checkIPv4(uint32_t* ip){
    uint64_t* value = ipv4Blacklist.lookup(ip);
    if(value){
        *value += 1;
        return 1;
    }
    return 0;
}

static inline int checkIPv6(unsigned __int128* ipv6){
    //uint64_t val = 0;
    uint64_t* value = ipv6Blacklist.lookup(ipv6);
    if(value){
        *value += 1;
        return 1;
    }
    return 0;
}

static inline int checkMac(uint64_t* mac){
    uint64_t* value = macBlacklist.lookup(mac);
    if(value){
        *value += 1;
        return 1;
    }
    return 0;
}

int xdp_prog1(struct CTXTYPE *ctx) {
    void* data_end = (void*)(long)ctx->data_end;
    void* data = (void*)(long)ctx->data;

    struct ethhdr *eth = data;
    int rc = RETURNCODE;
    uint16_t h_proto;
    uint64_t nh_off = 0;
    nh_off = sizeof(*eth);

    if (data + nh_off  > data_end)
        return rc;

    uint64_t macIn = mac2u64(eth->h_source);
    uint64_t macEg = mac2u64(eth->h_dest);
    if(checkMac(&macIn) || checkMac(&macEg)){
        return rc;
    }

    h_proto = eth->h_proto;


    if (h_proto == htons(ETH_P_8021Q) || h_proto == htons(ETH_P_8021AD)) {
        struct vlan_hdr *vhdr;
        vhdr = data + nh_off;
        nh_off += sizeof(struct vlan_hdr);
        if (data + nh_off > data_end)
            return rc;
        h_proto = vhdr->h_vlan_encapsulated_proto;
    }

    if (h_proto == htons(ETH_P_IP)){
        uint32_t ipEg = 0;
        uint32_t ipIn = 0;
        if(parse_ipv4_ip(data, nh_off, data_end, &ipEg, &ipIn)){
            if (checkIPv4(&ipEg) || checkIPv4(&ipIn))
                return rc;
        }
    } else{
        if (h_proto == htons(ETH_P_IPV6)){
            //to test: ping6 fe80::%<interface>
            unsigned __int128 ipv6Eg = 0;
            unsigned __int128 ipv6In = 0;
            if(parse_ipv6_ip(data, nh_off, data_end, &ipv6Eg, &ipv6In)){
                if(checkIPv6(&ipv6Eg) || checkIPv6(&ipv6In))
                    return rc;
            }
        }
    }
    
    return XDP_PASS;
}
""", cflags=["-w", "-DRETURNCODE=%s" % ret, "-DCTXTYPE=%s" % ctxtype])

def mac2int(mac):
    macVal=mac.split(':')
    mac=""
    for i in range(len(macVal)):
        mac+=macVal[i]
    return int(mac,16)

def hex2Mac(macHex):
    macHex=macHex[2:]
    diff = 12 - len(macHex)
    macHex = ("0"*diff) + macHex
    mac=""
    for i in range(6):
        mac += macHex[2*i:2*i+2]+":"
    return mac[:-1]


def inject(dev):
    global blockIpv4
    global blockIpv6
    global blockMac
    global device
    
    device=dev
    fn = b.load_func("xdp_prog1", mode)
    b.attach_xdp(device, fn, flags)
    blockIpv4 = b.get_table("ipv4Blacklist")
    blockMac= b.get_table("macBlacklist")
    blockIpv6 =b.get_table("ipv6Blacklist")


def block(addresses):
    for address in addresses:
        
        if(address.find('ipv4') != -1):
            #pton cambia ordine in big-endian
            #I: unsigned int
            address = unpack("I",inet_pton(AF_INET, address[4:]))[0] 

            ini = blockIpv4.Leaf()
            for i in range(0, multiprocessing.cpu_count()):
                ini[i] = 0
            blockIpv4[blockIpv4.Key(address)] = ini
    
    
        elif (address.find('mac')!=-1):
                ini = blockMac.Leaf()
                for i in range(0, multiprocessing.cpu_count()):
                    ini[i] = 0
                blockMac[blockMac.Key(mac2int(address[3:]))] = ini
    
        else:
            a,c =unpack("QQ",inet_pton(AF_INET6, address[4:]))
            ini = blockIpv6.Leaf()
            for i in range(0, multiprocessing.cpu_count()):
                ini[i] = 0
            arr = blockIpv6.Key()
            arr[0] = a
            arr[1] = c
            blockIpv6[arr] = ini


def blocked():
    print("\n")
    while(True):
        try:
            for k in blockIpv4.keys():
                val = blockIpv4.sum(k).value

                #I unsigned int
                #ntoa cambia ordine in little-endian
                i = inet_ntoa(pack("I", k.value))
                print("%-30s %-4d pkts" %(i, val))
        
            for k in blockMac.keys():
                val = blockMac.sum(k).value
                print("%-30s %-4d pkts" %(hex2Mac(hex(k.value)), val))
        
            for k in blockIpv6.keys():
                val = blockIpv6.sum(k).value
                i = inet_ntop(AF_INET6, pack("Q",k[0])+pack("Q",k[1]))
                print("%-30s %-4d pkts" %(i, val))

            time.sleep(30)
        except KeyboardInterrupt:
            return


def eject():
    b.remove_xdp(device, flags)
