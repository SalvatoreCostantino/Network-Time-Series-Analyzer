dim_vlset  = 168 #1 week
period = 50 #4h 
num_points5m = 400 #33h
p_rate = 0.65
influxHost = 'localhost'
influxPort = 8086
#start_time = "'2019-06-25T17:28:00Z'"
start_time = "'2019-04-18T17:28:00Z'"
RSI_treshold = 90
prophet_mul = 1.2
zeroKiller = 0.000000000000000000001
interfaces=["1"]
prophet_diagnostic = None
verbose = True
precision = 1000
minuteProphet = ":02"
checkCat = None
device = "wlp2s0"
hostTrailer = 4
predictedPoint = 4
num_points1h = 504 + predictedPoint # about 3 weeks
showGraph = True
flooding_treshold = 2.5
ratio_treshold = 0.85
packet_size_treshold = 550
maxLine = 6
mitigation = False
graphDir = "graph/"



measurements1h =        {"P0":
                                {"host:traffic" : 
                                        {"name":       "bytes_fldng_atk", 
                                        "metric":      "bytes_sent"},
                        
                                "host:traffic ":
                                        {"name":       "bytes_fldng_vct",
                                        "metric":      "bytes_rcvd"}
                                
                                },
                        "P1": 
                                {"host:total_flows": 
                                        {"name":       "flows_fldng_atk", 
                                        "metric":      "flows_as_client"},
                        
                                "host:total_flows ":
                                        {"name":       "flows_fldng_vct", 
                                        "metric":      "flows_as_server"}
                                }
                        }
                        

measurements5m =        {"mac:arp_rqst_sent_rcvd_rpls" : 
                                {"name":        "net_scan_atk", 
                                "metrics":      [["request_packets_sent"], ["reply_packets_rcvd"]],
                                "minValue":     [2/300, 2/300]},
                    
                        "host:echo_reply_packets host:echo_packets" :
                                {"name":        "ping_flooding", 
                                "metrics":      [["packets_rcvd"], ['packets_sent']],
                                "minValue":     [8/300, 8/300]},
                    
                        "host:dns_qry_sent_rsp_rcvd": 
                                {"name":        "dns_flooding", 
                                "metrics":      [["replies_ok_packets","replies_error_packets"], ["queries_packets"]],
                                "minValue":     [8/300, 8/300]},
                    
                        "host:dns_qry_sent_rsp_rcvd ": 
                                { "name":       "dns_errors", 
                                "metrics":      [["replies_error_packets"],["replies_ok_packets"]],
                                "minValue":     [8/300, 8/300]},
                    
                        "host:unreachable_flows host:total_flows": 
                                {"name":        "port_scan_atk", 
                                "metrics":      [["flows_as_server"], ["flows_as_client"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:unreachable_flows  host:total_flows": 
                                {"name":        "port_scan_vct", 
                                "metrics":      [["flows_as_client"], ["flows_as_server"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:host_unreachable_flows host:total_flows": 
                                {"name":        "ip_probing_vct", 
                                "metrics":      [["flows_as_client"], ["flows_as_server"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:host_unreachable_flows  host:total_flows": 
                                {"name":        "ip_probing_atk", 
                                "metrics":      [["flows_as_server"], ["flows_as_client"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:tcp_tx_stats host:tcp_packets": 
                                {"name":        "TCP_client_iss", 
                                "metrics":      [["lost_packets","out_of_order_packets","retransmission_packets"],["packets_sent"]],
                                "minValue":     [15/300, 45/300]},
                    
                        "host:tcp_rx_stats host:tcp_packets" : 
                                {"name":        "TCP_server_iss", 
                                "metrics":      [["lost_packets","out_of_order_packets","retransmission_packets"],["packets_rcvd"]],
                                "minValue":     [15/300, 45/300]},
                        
                        "host:DNS_traffic host:dns_qry_sent_rsp_rcvd host:dns_qry_rcvd_rsp_sent": 
                                {"name":        "dns_infiltration", 
                                "metrics":      [["bytes_rcvd"],["replies_ok_packets","replies_error_packets"],["queries_packets"]],
                                "minValue":     [2000/300, 8/300]},
                        
                        "host:DNS_traffic  host:dns_qry_sent_rsp_rcvd host:dns_qry_rcvd_rsp_sent" : 
                                {"name":        "dns_exfiltration", 
                                "metrics":      [["bytes_sent"],["queries_packets"],["replies_ok_packets","replies_error_packets"]],
                                "minValue":     [2000/300, 8/300]},
                        
                        "host:anomalous_flows host:total_flows" :
                                {"name":        "anmls_flows_vct",
                                "metrics":      [["flows_as_server"],["flows_as_server"]],
                                "minValue":     [3/300, 12/300]},

                        "host:anomalous_flows  host:total_flows" :
                                {"name":        "anmls_flows_atk",
                                "metrics":      [["flows_as_client"],["flows_as_client"]],
                                "minValue":     [3/300, 3/300]},
                        }


categories = ["RemoteAccess", "Unspecified", "Mining", "Malware"]

scoreTable = {  "net_scan_atk"          :0.10,
                "ping_flooding"         :0.25,
                "dns_flooding"          :0.25,
                "dns_errors"            :0.10,
                "port_scan_atk"         :0.25,
                "port_scan_vct"         :0.25,
                "ip_probing_vct"        :0.25,
                "ip_probing_atk"        :0.25,
                "TCP_client_iss"        :0.05,
                "TCP_server_iss"        :0.05,
                "dns_infiltration"      :0.20,
                "dns_exfiltration"      :0.20,
                "anmls_flows_atk"       :0.25,
                "anmls_flows_vct"       :0.25,
                "flows_fldng_vct"       :0.30,
                "flows_fldng_atk"       :0.30,
                "bytes_fldng_vct"       :0.30,
                "bytes_fldng_atk"       :0.30,
                "cntc_fld_atk"          :0.30,
                "cntc_fld_vct"          :0.30,
                "act_flw_fld_atk"       :0.30,
                "act_flw_fld_vct"       :0.30,
        }

