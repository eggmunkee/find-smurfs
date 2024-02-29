# Find Smurfs

Find the smurfs residing in an FEC contributions csv file.

![Find Smurfs Window](docs/img/find_smurfs_screenshot.png)

## Usage

Run without arguments to use GUI
> or
`python find_smurfs.py <contributions_csv_file_path>`

## Example - Sam Brown for US Senate Results:

[Sam Brown Results](docs/example_sam_brown_ussenate.txt)

## Columns Required

* contributor_last_name
* contributor_first_name
* contributor_employer
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
