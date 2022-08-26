import argparse
import sys
import linecache
import traceback
import datetime
import gzip
class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def parse_args():
    parser= MyParser(description='This script saves the first n reads of a fastq.gz file')
    parser.add_argument('--fqgz',required=True, default="", type=str, help='path to a fastq.gz file', metavar='')
    parser.add_argument('--n',required=False, default="100000", type=int, help='number of reads to retain', metavar='')
    config = parser.parse_args()
    return(config)

config = vars(parse_args())

#####################
##      main       ##
#####################    
def main():
    try: 
        starttime = datetime.datetime.now()
        read_count = 0
        with gzip.open(config["fqgz"], "rt") as fh, gzip.open(config["fqgz"].rstrip(".fastq.gz") + ".downsize.fastq.gz", "wt") as wfh:
            lines = []
            for line in fh:
                lines.append(line.rstrip())
                if len(lines) == 4:
                    wfh.write("\n".join(lines))
                    wfh.write("\n")
                    lines = []
                    read_count+=1
                    if read_count>= config["n"]:
                        break

        endtime = datetime.datetime.now()
        elapsed_sec = endtime - starttime
        elapsed_min = elapsed_sec.seconds / 60
        print(f"elapsed time {elapsed_min:.2f} min ({elapsed_sec} sec)")

    except Exception  as e:
        print("Unexpected error:", str(sys.exc_info()))
        traceback.print_exc()
        print("additional information:", e)
        PrintException()

##########################
## function definitions ##
##########################


def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

    
if __name__ == "__main__": main()    
