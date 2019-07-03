import argparse

examples = """examples:
    ./net_tisean.py                             # only RSI an treshold diagnostic
    ./net_tisean.py -x -v -f results.txt        # prints to file all informaztions and executes mitigation 
    ./net_tisean.py -p -g -d myDir              # saves prophet graphs in a specific directory
    ./net_tisean.py -p -c -g                    # uses prophet, checks NDPI categories and saves graphs
    ./net_tisean.py -t '2019-06-28T17:28:00Z'   # analisys time. if not specified, the real time analisys will start   
"""

def parseArg():
    parser = argparse.ArgumentParser(
        description="Time Series Analizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples)
    parser.add_argument("-c", "--cat",
        help="check ndpi categories", action='store_true')
    parser.add_argument("-p", "--prophet",
        help="prophet diagnostic",  action='store_true')
    parser.add_argument("-g", "--graph",
        help="save prophet graph",  action='store_true')
    parser.add_argument("-v", "--verbose",
        help="save prophet graph",  action='store_true')
    parser.add_argument("-x", "--xdp",
        help="active xdp mitigation",  action='store_true')
    parser.add_argument("-f", "--file",
        help="output file")
    parser.add_argument("-d", "--dir",
        help="graphs directory")
    parser.add_argument("-t", "--time",
        help="analysis date")
    args = parser.parse_args()
    return args