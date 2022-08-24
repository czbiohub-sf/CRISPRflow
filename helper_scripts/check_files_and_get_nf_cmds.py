import argparse
from genericpath import isfile
import sys
import linecache
import pandas as pd
import os

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def parse_args():
    parser = MyParser(description='This script checks the files specified in the excel file')
    parser.add_argument('--csv', default="", type=str, help='path to the csv file', metavar = '')
    config = parser.parse_args()
    if len(sys.argv) == 1:  # print help message if arguments are not valid
        parser.print_help()
        sys.exit(1)
    return config


config = vars(parse_args())
csv = config['csv']

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#####################
##      main       ##
#####################
def main():
    try:
        print("begin checking files")
        red_flag = False
        df = pd.read_csv(config['csv'])
        with open(f"{csv}.sh", "w") as wfh:
            for index, row in df.iterrows():
                Parent_dir=row['Parent_dir']
                Lib_A_dir=row['Lib_A_dir']
                Lib_B_dir=row['Lib_B_dir']
                Lib_A_csv=row['Lib_A_csv']
                Lib_B_csv=row['Lib_B_csv']
                prefix=row['prefix']
                suffix_tr=row['suffix_tr']
                suffix_ctrl=row['suffix_ctrl']

                #check library files
                if not pd.isnull(row['Lib_A_csv']):
                    path = os.path.join(Parent_dir,Lib_A_dir,Lib_A_csv)
                    if not os.path.isfile(path):
                        print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                        red_flag = True
                    else:
                        print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")

                if not pd.isnull(row['Lib_B_csv']):
                    path = os.path.join(Parent_dir,Lib_B_dir,Lib_B_csv)
                    if not os.path.isfile(path):
                        print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                        red_flag = True
                    else:
                        print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")          
                #check fastq files    
                #treatment            
                if not pd.isnull(row["Lib_A_tr_bio_reps"]):
                    A_tr_bio_reps = row["Lib_A_tr_bio_reps"].split(",")
                    for rep in A_tr_bio_reps:
                        path = os.path.join(Parent_dir,Lib_A_dir, f"{prefix}{rep}{suffix_tr}")
                        if not os.path.isfile(path):
                            print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                            red_flag = True
                        else:
                            print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")
                #treatment
                if not pd.isnull(row["Lib_B_tr_bio_reps"]):
                    B_tr_bio_reps = row["Lib_B_tr_bio_reps"].split(",")
                    for rep in B_tr_bio_reps:
                        path = os.path.join(Parent_dir,Lib_B_dir, f"{prefix}{rep}{suffix_tr}")
                        if not os.path.isfile(path):
                            print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                            red_flag = True
                        else:
                            print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")                  
                #ctrl
                if not pd.isnull(row["Lib_A_ctrl_bio_reps"]):
                    A_ctrl_bio_reps = row["Lib_A_ctrl_bio_reps"].split(",")
                    for rep in A_ctrl_bio_reps:
                        path = os.path.join(Parent_dir,Lib_A_dir, f"{prefix}{rep}{suffix_ctrl}")
                        if not os.path.isfile(path):
                            print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                            red_flag = True
                        else:
                            print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")                      
                #ctrl
                if not pd.isnull(row["Lib_B_ctrl_bio_reps"]):
                    B_ctrl_bio_reps = row["Lib_B_ctrl_bio_reps"].split(",")
                    for rep in B_ctrl_bio_reps:
                        path = os.path.join(Parent_dir,Lib_B_dir, f"{prefix}{rep}{suffix_ctrl}")
                        if not os.path.isfile(path):
                            print(f"{path} {bcolors.FAIL}not found{bcolors.ENDC}")
                            red_flag = True
                        else:
                            print(f"{path} {bcolors.OKGREEN}OK{bcolors.ENDC}")              
            
        print("done checking files")
        if red_flag == True:
            print(f"failed file check, please make sure all files are accessible and rerun this script")
        else:
            print(f"passed file check, generating Nextflow commands...")
            df = pd.read_csv(config['csv'])
            with open(f"{csv}.sh", "w") as wfh:
                for index, row in df.iterrows():
                    # wfh.write("declare -a Lib_A=(")
                    # reps = " ".join(['"' + item + '"' for item in reps])
                    # wfh.write(f"{reps})\n")
                    if not pd.isnull(row["Lib_A_tr_bio_reps"]):
                        wfh.write('\n#########')
                        wfh.write(f" {row['prefix']} ")
                        wfh.write('#########\n')
                        wfh.write(f"Lib_A_dir={row['Parent_dir']}/{row['Lib_A_dir']}/\n")
                        wfh.write(f"Lib_B_dir={row['Parent_dir']}/{row['Lib_B_dir']}/\n")
                        wfh.write(f"Lib_A_csv={row['Lib_A_csv']}\n")
                        wfh.write(f"Lib_B_csv={row['Lib_B_csv']}\n")
                        wfh.write(f"prefix={row['prefix']}\n")
                        wfh.write(f"suffix_tr={row['suffix_tr']}\n")
                        wfh.write(f"suffix_ctrl={row['suffix_ctrl']}\n")

                        A_tr_bio_reps = row["Lib_A_tr_bio_reps"].split(",")
                        A_bio_tr_fqs = ""
                        for rep in A_tr_bio_reps:
                            A_bio_tr_fqs = A_bio_tr_fqs + "${Lib_A_dir}${prefix}" + f"{rep}" + "${suffix_tr},"

                        A_ctrl_bio_reps = row["Lib_A_ctrl_bio_reps"].split(",")
                        A_bio_ctrl_fqs = ""
                        for rep in A_ctrl_bio_reps:
                            A_bio_ctrl_fqs = A_bio_ctrl_fqs + "${Lib_A_dir}${prefix}" + f"{rep}" + "${suffix_ctrl},"

                        A_bio_tr_fqs = A_bio_tr_fqs.rstrip(",")
                        A_bio_ctrl_fqs = A_bio_ctrl_fqs.rstrip(",")

                        if not pd.isnull(row["Lib_B_dir"]): #use libA and libB
                            B_tr_bio_reps = row["Lib_B_tr_bio_reps"].split(",")
                            B_bio_tr_fqs = ""
                            for rep in B_tr_bio_reps:
                                B_bio_tr_fqs = B_bio_tr_fqs + "${Lib_B_dir}${prefix}" + f"{rep}" + "${suffix_tr},"

                            B_ctrl_bio_reps = row["Lib_B_ctrl_bio_reps"].split(",")
                            B_bio_ctrl_fqs = ""
                            for rep in B_ctrl_bio_reps:
                                B_bio_ctrl_fqs = B_bio_ctrl_fqs + "${Lib_B_dir}${prefix}" + f"{rep}" + "${suffix_ctrl},"

                            B_bio_tr_fqs = B_bio_tr_fqs.rstrip(",")
                            B_bio_ctrl_fqs = B_bio_ctrl_fqs.rstrip(",")

                            # wfh.write("declare -a Lib_B=(")
                            # reps = row["Lib_B_bio_reps"].split(",")
                            # reps = " ".join(['"' + item + '"' for item in reps])
                            # wfh.write(f"{reps})\n")

                            # wfh.write(
                            #     '\n# extract and concat libA rep fastq files\n'
                            #     'rm "${Lib_A_dir}${prefix}A${suffix_tr}.fq"\n'
                            #     'for str in ${Lib_A[@]}; do\n'
                            #     '    gunzip -c "${Lib_A_dir}${prefix}${str}${suffix_tr}" >> "${Lib_A_dir}${prefix}A${suffix_tr}.fq"\n'
                            #     'done\n'
                            #     'gzip -c "${Lib_A_dir}${prefix}A${suffix_tr}.fq" > "${Lib_A_dir}${prefix}A${suffix_tr}"\n'
                            #     'rm "${Lib_A_dir}${prefix}A${suffix_tr}.fq"\n'
                            # )
                            # wfh.write(
                            #     '\n# extract and concat rep libB fastq files\n'
                            #     'rm "${Lib_B_dir}${prefix}B${suffix_tr}.fq"\n'
                            #     'for str in ${Lib_B[@]}; do\n'
                            #     '    gunzip -c "${Lib_B_dir}${prefix}${str}${suffix_tr}" >> "${Lib_B_dir}${prefix}B${suffix_tr}.fq"\n'
                            #     'done\n'
                            #     'gzip -c "${Lib_B_dir}${prefix}B${suffix_tr}.fq" > "${Lib_B_dir}${prefix}B${suffix_tr}"\n'
                            #     'rm "${Lib_B_dir}${prefix}B${suffix_tr}.fq"\n'
                            # )
                            tr_fasqs = ""
                            #for i in

                            wfh.write(
                                '\n./nextflow run main.nf --treatment_fastq '
                                f"{A_bio_tr_fqs},{B_bio_tr_fqs}"
                                ' \\\n'
                                '--control_fastq '
                                f"{A_bio_ctrl_fqs},{B_bio_ctrl_fqs}"
                                ' \\\n'
                                '--library ${Lib_A_dir}${Lib_A_csv},${Lib_B_dir}${Lib_B_csv} \\\n'
                                '--output mageck_out --output_prefix ${prefix} -profile testing\n'
                            )

                        else:
                            # wfh.write(
                            #     '\n# extract and concat rep fastq files\n'
                            #     'rm "${Lib_A_dir}${prefix}A${suffix_tr}.fq"\n'
                            #     'for str in ${Lib_A[@]}; do\n'
                            #     '    gunzip -c "${Lib_A_dir}${prefix}${str}${suffix_tr}" >> "${Lib_A_dir}${prefix}all${suffix_tr}.fq"\n'
                            #     'done\n'
                            #     'gzip -c "${Lib_A_dir}${prefix}all${suffix_tr}.fq" > "${Lib_A_dir}${prefix}all${suffix_tr}"\n'
                            #     'rm "${Lib_A_dir}${prefix}A${suffix_tr}.fq"\n'
                            # )
                            wfh.write(
                                '\n./nextflow run main.nf --treatment_fastq '
                                f"{A_bio_tr_fqs}"
                                ' \\\n'
                                '--control_fastq '
                                f"{A_bio_ctrl_fqs}"
                                ' \\\n'
                                '--library ${Lib_A_dir}${Lib_A_csv} \\\n'
                                '--output mageck_out --output_prefix ${prefix} -profile testing\n'
                            )
            print(f"wrote nf commands to file: {csv}.sh")
            print(f"moving {csv}.sh to the parent folder (of directory \"helper_scripts\")")
            os.rename(f"{csv}.sh",f"../{csv}.sh")



    except Exception as e:
        print("Unexpected error:", str(sys.exc_info()))
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
