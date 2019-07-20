import os, time, pyshark
from ipaddress import ip_network, ip_address

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print('iniciando...')

ip_whitelist = set()
cidr_blacklist = set()

with open('/root/softlayer_cidrs.txt') as f:
    softlayer_cidrs = f.readlines()
softlayer_cidrs = set([line.strip() for line in softlayer_cidrs])
softlayer_cidrs = set([ip_network(cidr) for cidr in softlayer_cidrs])

capture = pyshark.LiveCapture('wlan0', bpf_filter='tcp and not src net 192.168.12 and dst net 192.168.12')

print(bcolors.HEADER,'Firewall anti-Whatsapp iniciado',bcolors.ENDC)

for packet in capture.sniff_continuously():
    if packet['ip'].src in ip_whitelist:
        continue

    ip_src = ip_address(packet['ip'].src)

    for cidr in cidr_blacklist:
        if ip_src in cidr:
            print(bcolors.FAIL,packet['ip'].src,'JA BLOQUEADO',bcolors.ENDC)
            continue

    print(packet['ip'].src,'examinando...')
    ip_ok = True
    for cidr in softlayer_cidrs:
        if ip_src in cidr:
            ip_ok = False
            print(bcolors.WARNING,packet['ip'].src,'Whatsapp detectado!',bcolors.ENDC)
            if os.system('iptables -A FORWARD -s '+ str(cidr) +' -p tcp -j DROP') == 0:
                print(bcolors.WARNING,packet['ip'].src,'BLOQUEADO COM',str(cidr),bcolors.ENDC)
            else:
                print(bcolors.FAIL,packet['ip'].src,'FALHA AO BLOQUEAR',bcolors.ENDC)
            break
    if ip_ok:
        print(bcolors.OKGREEN, packet['ip'].src, 'liberado',bcolors.ENDC)
        ip_whitelist.add(packet['ip'].src)
    else:
        cidr_blacklist.add(cidr)
        softlayer_cidrs.discard(cidr)