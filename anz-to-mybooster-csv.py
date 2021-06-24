import argparse
import logging
import os
import sys
import pandas as pd
from datetime import datetime

"""
Usage: run.py [-h] -i --input-file [-f --output-filename] [-cc] [-d]

Provide anz bank statement and it will concat the fields to create a concatenated description field  

optional arguments:
  -h, --help            show this help message and exit
  -i --input-file       The csv input file bank statement from ANZ
  -f --output-filename  filename of the output csv
  -cc                   Use this flag if it is a Credit Card input file
  -d                    Enable debug mode

"""


def init(argv):
    """
    Initialise the script by setting up the logger and arguments as variables
    """
    # create log dir
    if not os.path.exists('./logs'):
        os.makedirs('./logs')

        # Setup the logger
    logging.basicConfig(
        filename='./logs/run.py.log',
        filemode='a',
        format='%(asctime)s sev=%(levelname)s file=%(filename)s module=%(name)s func=%(funcName)s %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO
    )

    global start_time
    start_time = datetime.now()
    logging.info("START script: " + str(start_time))

    # Get the arguments
    parser = argparse.ArgumentParser(
        description='Provide anz bank statement and it will concat the fields to create a concatenated description field')
    parser.add_argument('-i', required=True, metavar='--input-file',
                        help="The csv input file bank statement from ANZ")
    parser.add_argument('-f', metavar='--output-filename',
                        help="filename of the output csv", default='output.csv')
    parser.add_argument('-cc', action="store_true",
                        help="Use this flag if it is a Credit Card input file", default=False)
    parser.add_argument('-d', action="store_true", help='Enable debug mode')
    args = parser.parse_args(argv)
    logging.info(args)

    # Set the variables from user input
    global input_filename, output_filename, is_cc_file
    input_filename = args.i
    output_filename = args.f
    is_cc_file = args.cc
    if args.d:
        logging.getLogger().setLevel(logging.DEBUG)


def end():
    """
    Close the script and output run time to log
    """
    global start_time
    run_time = datetime.now() - start_time
    logging.info("FINISH script with runtime of: " + str(run_time))


def main(argv):
    """
    Guts of the program, takes input, manipulates it and spits it back out
    """
    init(argv)

    # Get the filename again and read the csv
    try:
        global input_filename
        logging.info(input_filename)
        df = pd.read_csv(input_filename)
    except Exception as e:
        err_str = "Error while reading input csv file, check the logs for more..."
        print(err_str)
        logging.exception(err_str)
        print("Exiting script with errors.")
        quit()

    global is_cc_file
    try:
        if is_cc_file is False:
            # Set the headers we are concat for desc
            df['Description'] = df['Type'].map(str) + " " + df['Details'].map(str) + " " + \
                df['Particulars'].map(str) + " " + df['Code'].map(str) + \
                " " + df['Reference'].map(str)
            columns = ['Date', 'Description', 'Amount']
        else:
            # Set the cc headers we are concat for desc, there are less of them
            df['Description'] = df['Card'].map(
                str) + " " + df['Details'].map(str)
            columns = ['TransactionDate', 'Description', 'Amount']
    except KeyError as ke:
        err_str = "Error when creating new Description field, you probably forgot the -cc flag or included it for a non Credit Card file. Check logs for more details..."
        print(err_str)
        logging.exception(err_str)
        print("Exiting script with errors.")
        quit()

    # remove the comma and dollar sign
    df['Amount'] = df['Amount'].astype(str)
    df['Amount'] = df['Amount'].str.replace(',', '', regex=True)
    df['Amount'] = df['Amount'].str.replace('$', '', regex=True)

    # Set the columns to return back in the CSV file
    logging.debug(df[columns])

    global output_filename
    logging.info(output_filename)
    df.to_csv(output_filename,
              columns=columns, index=False)

    # Write out runtime and complete final tasks
    end()


if __name__ == "__main__":
    main(sys.argv[1:])
