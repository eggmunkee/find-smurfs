# Find Smurfs

Find the smurfs residing in an FEC contributions csv file.

![Find Smurfs Window](docs/img/find_smurfs_screenshot_v2.png)

# Prerequisite - Python3
## Install Python for Windows
The python installer for Windows is found below at the python website.

[Python Installs for Windows](https://www.python.org/downloads/windows/)

## Install Python for Mac OS
The python installer for Mac OS is found below at the python website.

[Python Installs for Mac](https://www.python.org/downloads/macos/)

### Install Python3 on Linux Mint for example:

Rough python3 dependencies install steps

`sudo apt install python3`

`sudo apt install python3-pip`

`pip install python3-tk`

To make usr/bin/python find python3 I used

`sudo apt install python-is-python3`

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
* Employer is Unemployed or Retired

> These options can be changed in options panel on the left side of the window. (GUI - graphical user interface only)

## Outputs

* 5+ count smurf identifiers to find the rows
* Total smurfing identities
* Total smurf transactions
* Transactions / Smurf identity
* Total smurfing amount
* Amount per Smurf
