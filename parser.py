import argparse

examples = """examples:
    ./net_tisean.py                             # print to default stdout and save graphs in default directory
    ./net_tisean.py -f results.txt              # print to file
    ./net_tisean.py -d myDir                    # save graphs in a specific directory
    ./net_tisean.py -f results.txt -d myDir     # print to file and save graphs in a specific directory
    ./net_tisean.py -p -c                       # use prophet e check NDPI categories
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
    parser.add_argument("-f", "--file",
        help="output file")
    parser.add_argument("-d", "--dir",
        help="graphs directory")
    parser.add_argument("-t", "--time",
        help="analysis date")
    args = parser.parse_args()
    return args