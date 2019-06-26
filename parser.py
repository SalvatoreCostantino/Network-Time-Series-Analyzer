import argparse

examples = """examples:
    ./net_tisean.py                             # print to default stdout and save graphs in default directory
    ./net_tisean.py -f results.txt              # print to file
    ./net_tisean.py -d myDir                    # save graphs in a specific directory
    ./net_tisean.py -f results.txt -d myDir     # print to file and save graphs in a specific directory   
"""

def parseArg():
    parser = argparse.ArgumentParser(
        description="Time Series Analizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=examples)
    parser.add_argument("-f", "--file",
        help="output file")
    parser.add_argument("-d", "--dir",
        help="graphs directory")
    args = parser.parse_args()
    return args