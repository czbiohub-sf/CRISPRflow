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
    parser.add_argument('--xlsx', default="", type=str, help='path to the xlsx file', metavar = '')
    config = parser.parse_args()
    if len(sys.argv) == 1:  # print help message if arguments are not valid
        parser.print_help()
        sys.exit(1)
    return config


config = vars(parse_args())
xlsx = config['xlsx']

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
        print("Begin checking files")
        red_flag = False

        #check input file path
        if not os.path.isfile(xlsx):
            sys.exit(f"Error: could not file file {xlsx}")

        #load spreadsheets
        try:
            df_info = pd.read_excel(xlsx, engine="openpyxl", sheet_name="Analysis_info")
        except:
            sys.exit("Error while reading sheet: Analysis_info")

        try:
            df_paths = pd.read_excel(xlsx, engine="openpyxl", sheet_name="File_paths")
        except:
            sys.exit("Error while reading sheet: Analysis_info")

        #check spreadsheets
        if df_info.shape[0] <= 5:
            sys.exit("Error: not enough rows in sheet: Analysis_info")
        if df_info.shape[1] <= 10:
            sys.exit("Error: not enough columns in sheet: Analysis_info")
        if df_paths.shape[0] <= 4:
            sys.exit("Error: not enough rows in sheet: File_paths")

        #check fastq files
        filepath_list = []
        for index, row in df_paths.iterrows():
            if index >= 3:
                filepath = row.iloc[0]
                filepath_list.append(filepath)
                if not os.path.isfile(filepath):
                    print(f"  {filepath} {bcolors.FAIL}not found{bcolors.ENDC}")
                    red_flag = True
                else:
                    print(f"  {filepath} {bcolors.OKGREEN}OK{bcolors.ENDC}")

        print("Done checking files")

        ################
        #parse metadata#
        ################
        print("Parsing metadata and generating commands for Nextflow")
        wfh = open(f"{xlsx}.sh", "w")

        #contrast
        contrast = df_info.iloc[0,1]
        fields = contrast.split(" vs ")
        if len(fields) < 2:
            sys.exit("Error parsing the contrast, make sure it's written as 'treatment vs control', single space only")
        tr = fields[0].strip()
        ctrl = fields[1].strip()
        #check if constrast is found in the table
        contrast_col = list(df_info.iloc[:,4])
        if tr in contrast_col and ctrl in contrast_col:
            pass
        else:
            sys.exit("Error parsing the contrast, make sure the treatment and control specificed in line 2 are in the table (starting at line 5)")

        #associate files with treatment and control
        tr_file_list = []
        ctrl_file_list = []
        for file in filepath_list:
            flag_tr = file.find(tr)
            flag_ctrl = file.find(ctrl)
            if flag_tr == -1 and flag_ctrl == -1:
                sys.exit(f"ERROR: neither {tr} or {ctrl} is in filename: {file}")
            if flag_tr != -1 and flag_ctrl != -1:
                sys.exit(f"ERROR: Both {tr} and {ctrl} is in filename: {file}")
            if flag_tr != -1:
                tr_file_list.append(file)
            else:
                ctrl_file_list.append(file)

        #Parse and check library
        lib_col = list(df_info.iloc[4:,6])
        for lib in lib_col: #check if invalid entry
            if not lib in ["Full", "splitA", "splitB"]:
                sys.exit(f"Error: library {lib} is not one of: Full, splitA, splitB (caps sensitive)")
        if "Full" in lib_col and ("splitA" in lib_col or "splitB" in lib_col):  #check if full and split coexists
            sys.exit(f"Error: Can't decide if using Full or split libraries")
        if ("splitA" in lib_col and not "splitB" in lib_col) or ( not "splitA" in lib_col and "splitB" in lib_col):
            sys.exit(f"Error: Can't have only splitA or splitB, please use Full instead")
        #fqs
        tr_fqs = ",".join(tr_file_list)
        ctrl_fqs = ",".join(ctrl_file_list)
        #library file
        library_path_input = df_paths.iloc[0,0].split(";")
        library_path_input = [i for i in library_path_input if i] # remove empty items
        if "Full" in lib_col:
            if len(library_path_input)>=2:
                sys.exit("ERROR: Full library specified, but you entered two file paths for the library reference")
            lib_ref_file = library_path_input[0]
        else:
            if len(library_path_input)==1:
                sys.exit("ERROR: Split library specified, but you entered one file paths for the library reference")
            lib_ref_file = f"{library_path_input[0]},{library_path_input[1]}"

        #etc metadata
        Lastname1=df_info.iloc[4,0]
        Lastname2=df_info.iloc[4,1]
        VirusInfo=df_info.iloc[4,2]
        Host=df_info.iloc[4,3]
        Library=df_info.iloc[4,5]
        reps=df_info.iloc[1,1].replace(';','-')

        analysis_name = f"{Lastname1}_{Lastname2}_{VirusInfo}_{Host}_{Library}_{reps}_{tr}_vs_{ctrl}"
        print(f"Analysis name is {bcolors.OKCYAN}{analysis_name}{bcolors.ENDC} ")

        #####################
        #generate nf command#
        #####################

        if red_flag == True:
            print(f"failed file check and/or metadata parsing, please fix issues and rerun this script")
        else:
            print(f"passed file check and successfully parsed metadata, generating Nextflow commands...")
            wfh.write(f"###############\n")
            wfh.write(f"#Analysis name: {analysis_name}\n")
            wfh.write(f"###############\n")

            wfh.write(
                '\n./nextflow run main.nf --treatment_fastq '
                f"{tr_fqs}"
                ' \\\n'
                '--control_fastq '
                f"{ctrl_fqs}"
                ' \\\n'
                f"--library {lib_ref_file}"
                ' \\\n'
                f"--output mageck_out --output_prefix {analysis_name} -profile testing\n")

        wfh.close()
        print(f"wrote nf commands to file: {xlsx}.sh")
        print(f"moving {xlsx}.sh from metadata folder to the parent folder")
        #move sh file to the parent folder
        csv_filename = os.path.basename(f"{xlsx}.sh")
        if os.path.isfile(csv_filename):
            os.remove(csv_filename)
        os.rename(f"{xlsx}.sh",f"{csv_filename}")

        print(f"{bcolors.OKGREEN}Done!{bcolors.ENDC}")

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
