# Find Smurfs

Find the smurfs residing in an FEC contributions csv file.

## Usage

`python find_smurfs.py <contributions_csv_file_path>`

## Columns Required

* contributor_last_name
* contributor_first_name
* contributor_zip
* contributor_receipt_amount

## What is included as a smurf

* Dollar amount less than 200
* 5 or more transactions of the same amount

## Outputs

* 5+ count smurf identifiers to find the rows
* Total smurfing identities
* Total smurf transactions
* Transactions / Smurf identity
* Total smurfing amount
* Amount per Smurf
