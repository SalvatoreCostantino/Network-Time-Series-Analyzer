dim_vlset  = 168 #1 week
period = 50 #4h 
num_points5m = 400 #33h
p_rate = 0.70
influxHost = 'localhost'
influxPort = 8086
start_time = None
RSI_treshold = 80
zeroKiller = 0.000000000000000000001
interfaces=["0"]
prophet_diagnostic = False
verbose = False
precision = 1000
minuteProphet = ":02"
checkCat = False
device = "wlp2s0"
hostTrailer = 4
predictedPoint = 4
totPredPoint = predictedPoint * 3
num_points1h = 504 + predictedPoint # about 3 weeks
showGraph = False
flooding_treshold = 1
ratio_treshold = 0.50
packet_size_treshold = 576
maxLine = 6
mitigation = False
graphDir = "graph/"
validationTime = 2 * dim_vlset
limitRSI = 8000
limitProphet = 45




measurements1h =        {"P0":
                                {"host:traffic" : 
                                        {"metric":      "bytes_sent"},
                        
                                "host:traffic ":
                                        {"metric":      "bytes_rcvd"}
                                
                                },
                        "P1": 
                                {"host:total_flows": 
                                        {"metric":      "flows_as_client"},
                        
                                "host:total_flows ":
                                        {"metric":      "flows_as_server"}
                                }
                        }
                        

measurements5m =        {"mac:arp_rqst_sent_rcvd_rpls" : 
                                {"name":        "arp_packets", 
                                "metrics":      [["request_packets_sent"], ["reply_packets_rcvd"]],
                                "minValue":     [2/300, 2/300]},
                    
                        "host:echo_reply_packets host:echo_packets" :
                                {"name":        "ping_packets", 
                                "metrics":      [["packets_rcvd"], ['packets_sent']],
                                "minValue":     [8/300, 8/300]},
                    
                        "host:dns_qry_sent_rsp_rcvd": 
                                {"name":        "dns_packets", 
                                "metrics":      [["replies_ok_packets","replies_error_packets"], ["queries_packets"]],
                                "minValue":     [8/300, 8/300]},
                    
                        "host:dns_qry_sent_rsp_rcvd ": 
                                { "name":       "dns_errors", 
                                "metrics":      [["replies_error_packets"],["replies_ok_packets","replies_error_packets"]],
                                "minValue":     [6/300, 8/300]},
                    
                        "host:unreachable_flows host:total_flows": 
                                {"name":        "port_unreach_srv", 
                                "metrics":      [["flows_as_server"], ["flows_as_client"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:unreachable_flows  host:total_flows": 
                                {"name":        "port_unreach_clt", 
                                "metrics":      [["flows_as_client"], ["flows_as_server"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:host_unreachable_flows host:total_flows": 
                                {"name":        "host_unreach_clt", 
                                "metrics":      [["flows_as_client"], ["flows_as_server"]],
                                "minValue":     [2/300, 12/300]},
                    
                        "host:host_unreachable_flows  host:total_flows": 
                                {"name":        "host_unreach_srv", 
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
                                {"name":        "dns_size_srv", 
                                "metrics":      [["bytes_rcvd"],["replies_ok_packets","replies_error_packets"],["queries_packets"]],
                                "minValue":     [1000000, 8/300]},
                        
                        "host:DNS_traffic  host:dns_qry_sent_rsp_rcvd host:dns_qry_rcvd_rsp_sent" : 
                                {"name":        "dns_size_clt", 
                                "metrics":      [["bytes_sent"],["queries_packets"],["replies_ok_packets","replies_error_packets"]],
                                "minValue":     [1000000, 8/300]},
                        
                        "host:anomalous_flows host:total_flows" :
                                {"name":        "anmls_flows_srv",
                                "metrics":      [["flows_as_server"],["flows_as_server"]],
                                "minValue":     [3/300, 12/300]},

                        "host:anomalous_flows  host:total_flows" :
                                {"name":        "anmls_flows_clt",
                                "metrics":      [["flows_as_client"],["flows_as_client"]],
                                "minValue":     [3/300, 12/300]},
                        }


categories = ["RemoteAccess", "Unspecified", "Mining", "Malware"]

scoreTable = {  "arp_packets"           :0.10,
                "ping_packets"          :0.25,
                "dns_packets"           :0.25,
                "dns_errors"            :0.10,
                "port_unreach_clt"      :0.25,
                "port_unreach_srv"      :0.25,
                "host_unreach_clt"      :0.25,
                "host_unreach_srv"      :0.25,
                "TCP_client_iss"        :0.05,
                "TCP_server_iss"        :0.05,
                "dns_size_clt"          :0.20,
                "dns_size_srv"          :0.20,
                "anmls_flows_clt"       :0.25,
                "anmls_flows_srv"       :0.25,
                "flows_as_client"       :0.30,
                "flows_as_server"       :0.30,
                "bytes_sent"            :0.30,
                "bytes_rcvd"            :0.30,
        }

