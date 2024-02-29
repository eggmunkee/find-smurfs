#!/usr/bin/python

import csv
import tkinter as tk
from tkinter import filedialog, scrolledtext
from pathlib import Path
import tkinter.ttk as ttk
from tkinter.ttk import *

# initialize smurf stats and result data
def create_smurf_stats():
    return {
        "id_columns": ['contributor_last_name', 'contributor_first_name', 'contributor_employer', 'contributor_zip', 'contribution_receipt_amount'],
        "total_subset_count": 0,
        "total_subset_amount": 0.0,
        "small_donor_id_strings": {},
        "donation_max_threshold": 200.0,
        "donation_count_discard_threshold": 5,
        "records_processed": 0,
        "only_unemployed_or_retired": True
    }

def reset_stats(smurf_stats):
    smurf_stats['total_subset_count'] = 0
    smurf_stats['total_subset_amount'] = 0.0
    smurf_stats['small_donor_id_strings'] = {}
    smurf_stats['records_processed'] = 0

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
    try:
        record_amount = float(record['contribution_receipt_amount'])
    except ValueError:
        record_amount = 0.0
    smurf_stats['records_processed'] += 1
    if record_amount > 0.0 and record_amount < smurf_stats['donation_max_threshold']:
        smurf_id = get_smurf_id(smurf_stats, record)
        employer = ""
        if 'contributor_employer' in record:
            employer = record['contributor_employer']
        # only count unemployed or retired as smurfs
        is_retired_or_unemployed = employer.lower().find('unemployed') > -1 or employer.lower().find('retired') > -1
        if smurf_stats['only_unemployed_or_retired'] == False or is_retired_or_unemployed:
            if not (smurf_id in smurf_stats['small_donor_id_strings']):
                smurf_stats['small_donor_id_strings'][smurf_id] = 0
                #print("Smurf ID: " + smurf_id + "*")          
            smurf_stats['small_donor_id_strings'][smurf_id] += 1
            if smurf_stats['small_donor_id_strings'][smurf_id] % smurf_stats['donation_count_discard_threshold'] == 0:
                return "Smurf ID: " + smurf_id + " ... " + str(smurf_stats['small_donor_id_strings'][smurf_id]) + "x"
    return ""

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
            output = is_smurf(smurf_stats, record)
            if output:
                print(output)
        trim_sum_smurfs(smurf_stats)
        smurf_donor_count = smurf_stats['small_donor_id_strings'].__len__()
        print ("-----------------------------------------")
        print ("Total records processed:        " + str(smurf_stats['records_processed']))
        print ("Employment Filter (Only Retired/Unemmpoyed): " + str(smurf_stats['only_unemployed_or_retired']))
        print ("Total smurf count:              " + str(smurf_donor_count))
        print ("Total smurf transactions count: " + str(smurf_stats['total_subset_count']))
        if smurf_donor_count > 0:
            print ("Smurf transactions per smurf:   " + str(smurf_stats['total_subset_count'] / smurf_donor_count))
        print ("Total smurf dollar amount:      " + str(smurf_stats['total_subset_amount']))
        if smurf_donor_count > 0:
            print ("Smurf dollar amount per smurf:  " + str(smurf_stats['total_subset_amount'] / smurf_donor_count))

# The SyncCSVReadAndText class is a wrapper around the process of reading a CSV file and updating a text area with the results
#  It holds a generator to continue reading from the file while updating the text area and letting the UI respond
#  Instead of starting a process, it starts reading a file
#  The generator method calls a passed in callback to process the CSV row so that is_smurf, get_smurf_id, etc. can be used by the app logic
class SyncCSVReadAndText():
    def __init__(self, tk_app, log_area, process_cb, finished_cb):
        self.csv_file = ""
        self.app = tk_app
        self.log_area = log_area
        self.process_cb = process_cb
        self.finished_cb = finished_cb
        self.csv_gen = None
        self.file_obj = None

    def check_read(self):
        if self.csv_gen:
            self.app.update_idletasks()
            try:
                next(self.csv_gen)
            except StopIteration:
                pass

    def start_csv_read(self, csv_file):
        self.csv_file = csv_file
        self.file_obj = open(self.csv_file, 'rt')

        def csv_read():
            csvreader = csv.DictReader(self.file_obj)
            i = 0 # yield every x records
            for record in csvreader:
                self.process_cb(record)                
                if i % 5:
                    self.app.after(10, self.check_read)
                    yield
            self.stop_csv_read()
            self.finished_cb()

        self.csv_gen = csv_read()
        try:
            next(self.csv_gen)
        except StopIteration:
            pass

    def cancel_read(self):
        self.file_obj.close()
        self.file_obj = None
        self.csv_gen = None

        self.finished_cb()

    def stop_csv_read(self):
        if self.file_obj:
            self.file_obj.close()
        self.file_obj = None
        self.csv_gen = None

# The FindSmurfsApp is a TK App with the following UI widgets and features:
#  * In a top Frame:
#  * A file dialog to select a csv file, with a label showing the selected CSV file
#  * In a left side Frame:
#  * A button to start the process that says "Search For Smurfs"
#  * A button to cancel the process that says "Cancel"
#  * In the main layout, taking up the rest of the window:
#  * A scrolled text area to display the output
#  * A clear log button to clear the output area
#  * Uses the SyncCSVReadAndText class to read the CSV file and update the text area

class FindSmurfsApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Find Smurfs")
        self.geometry("900x700")

        self.csv_file = None
        self.csv_read = None
        self.log_area = None
        self.clear_log_button = None
        self.start_button = None
        self.cancel_button = None
        self.var_max_amount = tk.IntVar()
        self.var_count_threshold = tk.IntVar()
        self.var_retired_or_unemployed = tk.BooleanVar()

        self.smurf_stats = create_smurf_stats()

        self.create_widgets()

        self.sync_csv_read = SyncCSVReadAndText(self, self.log_area, self.process_record, self.finished_process)

    def create_widgets(self):
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#bbb", font=("Comic Sans", 12))
        self.style.configure("Primary.TButton", padding=6, relief="flat", background="#8ae")
        self.style.configure("Delete.TButton", padding=6, relief="flat", background="#e99")
        self.style.configure("TMain", padding=6, relief="groove", background="#bdf")
        self.style.configure("TFrame", padding=6, relief="groove", background="#bdf")
        self.style.configure("Smurf.TFrame", padding=6, relief="groove", background="#68d")
        self.style.configure("TLabel", padding=2, background="#68d", foreground="#fff")
        self.style.configure("TScrollbar", padding=2, background="#68d", foreground="#8ae")

        # ----------------------------------------------------

        self.top_frame = Frame(self, height=200, borderwidth=2, relief="groove")
        self.top_frame.pack(fill="x")

        self.file_type_label = Label(self.top_frame, text="Select CSV File")
        self.file_type_label.pack(padx=5, side="left")

        self.file_button = Button(self.top_frame, text="Select", command=self.select_csv_file, style="Primary.TButton")
        self.file_button.pack(padx=5, side="left")

        self.file_label = Label(self.top_frame, text="No file selected")
        self.file_label.pack(padx=5, side="left")

        # ----------------------------------------------------

        self.left_frame = Frame(self, width=200, borderwidth=2, relief="groove", style="Smurf.TFrame")
        self.left_frame.pack(side="left", fill="y")

        self.start_button = Button(self.left_frame, text="Search For Smurfs", command=self.start_process, style="Primary.TButton")
        self.start_button.pack(pady=5, side="top")
        self.start_button.config(state="disabled")

        self.cancel_button = Button(self.left_frame, text="Cancel", command=self.cancel_process, style="Delete.TButton")
        self.cancel_button.pack(pady=5, side="top")
        self.cancel_button.config(state="disabled")

        self.employment_filter_label = Label(self.left_frame, text="Employment Filter")
        self.employment_filter_label.pack(pady=5)
        self.employment_filter = Checkbutton(self.left_frame, text="Only Retired/Unemployed", variable=self.var_retired_or_unemployed, onvalue=True, offvalue=False)
        self.employment_filter.pack(pady=5)
        self.var_retired_or_unemployed.set(True)

        self.max_amount_label = Label(self.left_frame, text="Max Amount")
        self.max_amount_label.pack(pady=5)
        self.max_amount_entry = Spinbox(self.left_frame, from_=1, to=1000, textvariable=self.var_max_amount)
        self.max_amount_entry.pack(pady=5)
        self.var_max_amount.set(200)

        self.count_threshold_label = Label(self.left_frame, text="Count Threshold")
        self.count_threshold_label.pack(pady=5)
        self.count_threshold_entry = Spinbox(self.left_frame, from_=5, to=500, textvariable=self.var_count_threshold)
        self.count_threshold_entry.pack(pady=5)
        self.var_count_threshold.set(5)

        # ----------------------------------------------------

        self.log_frame = Frame(self, style="Smurf.TFrame")
        self.log_frame.pack(fill="both", expand=True)

        self.log_area = tk.Text(self.log_frame, wrap="none")
        vsb = Scrollbar(self.log_frame, command=self.log_area.yview, orient="vertical")
        hsb = Scrollbar(self.log_frame, command=self.log_area.xview, orient="horizontal")
        self.log_area.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.log_frame.grid_rowconfigure(0, weight=1)
        self.log_frame.grid_columnconfigure(0, weight=1)

        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.log_area.grid(row=0, column=0, sticky="nsew")

        # ---------------------------------------------------

        self.clear_log_button = Button(self.log_frame, text="Clear Log", command=self.clear_log, style="Delete.TButton")
        self.clear_log_button.grid(row=2, column=0, pady=5, sticky="s")
        #self.clear_log_button.pack(pady=5, side="bottom")

    def select_csv_file(self):
        self.csv_file = filedialog.askopenfilename()
        if self.csv_file:
            self.file_label.config(text="Selected: " + self.csv_file)
            self.start_button.config(state="normal")
        else:
            self.file_label.config(text="No file selected")
            self.start_button.config(state="disabled")

    def clear_log(self):
        self.log_area.delete('1.0', tk.END)

    def process_record(self, record):
        # process the record
        output = is_smurf(self.smurf_stats, record)
        if output:
            output = output.replace("|", " | ")
            self.log_area.insert(tk.END, output + "\n")
        if self.smurf_stats['records_processed'] % 500 == 0:
            self.log_area.insert(tk.END, "(" + str(self.smurf_stats['records_processed']) + "/?)\n")
        self.update_idletasks()

    def start_process(self):
        reset_stats(self.smurf_stats)
        self.smurf_stats['donation_max_threshold'] = float(self.var_max_amount.get())
        self.smurf_stats['donation_count_discard_threshold'] = int(self.var_count_threshold.get())
        self.smurf_stats['only_unemployed_or_retired'] = self.var_retired_or_unemployed.get()
        if self.csv_file:
            self.start_button.config(state="disabled")
            self.cancel_button.config(state="normal")
            self.log_area.insert(tk.END, "-----------------------------------------\n")
            self.log_area.insert(tk.END, "Starting process...\n")
            self.sync_csv_read.start_csv_read(self.csv_file)
        else:
            self.start_button.config(state="disabled") #disable the start button if no file is selected

    def cancel_process(self):
        self.sync_csv_read.cancel_read()
        self.start_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.log_area.insert(tk.END, "Process canceled\n")

    def finished_process(self):
        # final processing
        trim_sum_smurfs(self.smurf_stats)
        smurf_donor_count = self.smurf_stats['small_donor_id_strings'].__len__()

        # update UI
        self.start_button.config(state="normal")
        self.cancel_button.config(state="disabled")
        self.log_area.see(tk.END)

        # finished processing - output smurf stats
        self.log_area.insert(tk.END, "-----------------------------------------\n")
        self.log_area.insert(tk.END, "Total records processed:         " + str(self.smurf_stats['records_processed']) + "\n")
        self.log_area.insert(tk.END, "Employment Filter (Only Retired/Unemmpoyed): " + str(self.smurf_stats['only_unemployed_or_retired']) + "\n")
        self.log_area.insert(tk.END, "Total smurf count:               " + str(smurf_donor_count) + "\n")
        self.log_area.insert(tk.END, "Total smurf transactions count:  " + str(self.smurf_stats['total_subset_count']) + "\n")
        if smurf_donor_count > 0:
            self.log_area.insert(tk.END, "Smurf transactions per smurf:  " + str(self.smurf_stats['total_subset_count'] / smurf_donor_count) + "\n")
        self.log_area.insert(tk.END,     "Total smurf dollar amount:     " + str(self.smurf_stats['total_subset_amount']) + "\n")
        if smurf_donor_count > 0:
            self.log_area.insert(tk.END, "Smurf dollar amount per smurf: " + str(self.smurf_stats['total_subset_amount'] / smurf_donor_count) + "\n")
        self.log_area.see(tk.END)
        

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        main(sys.argv[1:])
    else:
        app = FindSmurfsApp()
        app.mainloop()