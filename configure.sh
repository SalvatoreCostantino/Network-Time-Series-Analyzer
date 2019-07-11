#!/bin/bash

influx -database "ntopng" -execute 'drop measurement "host:DNS_traffic"' 
influx -execute "SELECT * INTO ntopng.autogen.\"host:DNS_traffic\" FROM ntopng.autogen.\"host:ndpi\" WHERE protocol='DNS' GROUP BY *"
influx -database "ntopng" -execute 'drop measurement "host:p2p"' 
influx -execute "SELECT * INTO ntopng.autogen.\"host:p2p\" FROM ntopng.autogen.\"host:ndpi\" WHERE \
	protocol='BitTorrent' or \
	protocol='Gnutella' or \
	protocol='Thunder' or \
	protocol='Stealthnet' or \
	protocol='Soulseek' or \
	protocol='SMPP' or \
	protocol='OpenFT' or \
	protocol='FastTrack' or \
	protocol='eDonkey' or \
	protocol='DirectConnect' or \
	protocol='Direct_Download_Link' or \
	protocol='AppleJuice' or \
	protocol='Aimini' \
	GROUP BY *" 



