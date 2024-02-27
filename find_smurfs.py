#!/usr/bin/python

import csv

# initialize smurf stats and result data
def create_smurf_stats():
    return {
        "id_columns": ['contributor_last_name', 'contributor_first_name', 'contributor_zip', 'contribution_receipt_amount'],
        "total_subset_count": 0,
        "total_subset_amount": 0.0,
        "small_donor_id_strings": {},
        "donation_max_threshold": 200.0,
        "donation_count_discard_threshold": 5
    }
# get a unique id string for a record to compare across rows
def get_smurf_id(smurf_stats, record):
    id_string = ""
    for id_column in smurf_stats['id_columns']:
        id_string = id_string + '|' + record[id_column]
    return id_string[1:]

def pop_smurf_id_amount(smurf_stats, smurf_id):
    return float(smurf_id.split('|')[len(smurf_stats['id_columns']) - 1])

# check if a record is a smurf based on the max amount threshold and count in stats
def is_smurf(smurf_stats, record):
    record_amount = float(record['contribution_receipt_amount'])
    if record_amount > 0.0 and record_amount < smurf_stats['donation_max_threshold']:
        smurf_id = get_smurf_id(smurf_stats, record)
        if not smurf_id in smurf_stats['small_donor_id_strings']:
            smurf_stats['small_donor_id_strings'][smurf_id] = 0
            #print("Smurf ID: " + smurf_id + "*")  
        elif smurf_stats['small_donor_id_strings'][smurf_id] % smurf_stats['donation_count_discard_threshold'] == 0:
            print("Smurf ID: " + smurf_id + " ... " + str(smurf_stats['small_donor_id_strings'][smurf_id]) + "x")
        smurf_stats['small_donor_id_strings'][smurf_id] += 1

# go through the smurf candidate list and remove all below the count threshold
def trim_sum_smurfs(smurf_stats):
    small_donor_counts = smurf_stats['small_donor_id_strings']
    key_del_list = []
    for smurf_id in small_donor_counts:
        if small_donor_counts[smurf_id] < smurf_stats['donation_count_discard_threshold']:
            key_del_list.append(smurf_id)
            
    for key in key_del_list:
        del small_donor_counts[key]

    for smurf_id in small_donor_counts:
        smurf_stats['total_subset_count'] += small_donor_counts[smurf_id]
        smurf_stats['total_subset_amount'] += pop_smurf_id_amount(smurf_stats, smurf_id) * small_donor_counts[smurf_id]


# check if the program arguments are valid or output usage information
def check_args(program_args):
    if (len(program_args) < 1):
        print ("Usage: find_smurfs.py <csv file>")
        exit(1)
    
    return program_args[0]

# open the csv file, build column list, 
# find key columns, scan records, use stats to id smurfs
def main(args):
    smurf_stats = create_smurf_stats()
    csv_file = check_args(args)
    with open(csv_file, 'rt') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for record in csvreader:
            is_smurf(smurf_stats, record)
        trim_sum_smurfs(smurf_stats)
        smurf_donor_count = smurf_stats['small_donor_id_strings'].__len__()
        print ("-----------------------------------------")
        print ("Total smurf count: " + str(smurf_donor_count))
        print ("Total smurf transactions count: " + str(smurf_stats['total_subset_count']))
        print ("Smurf transactions per smurf: " + str(smurf_stats['total_subset_count'] / smurf_donor_count))
        print ("Total smurf dollar amount: " + str(smurf_stats['total_subset_amount']))
        print ("Smurf dollar amount per smurf: " + str(smurf_stats['total_subset_amount'] / smurf_donor_count))

if __name__ == "__main__":
    import sys
    main(sys.argv[1:])