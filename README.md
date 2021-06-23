# python-scripts
Repo to collate useful example python scripts in one place for future use.

## [anz-to-mybooster-csv.py](https://github.com/wjkw1/python-scripts/blob/main/anz-to-mybooster-csv.py)
Provide anz bank statement as input and it will concatenate the fields under new 'Description' label, and delete obsolete fields for [booster money management](https://my.booster.co.nz/Dashboard) app. See website here - https://booster.co.nz

**Usage:**
```
python3 run.py -i input-file.csv -f output-file.csv
```

## [men_and_mice_report.py](https://github.com/wjkw1/python-scripts/blob/main/men_and_mice_report.py)
This script gets range utilisation statistics using the Men and Mice Rest api

**Usage:**

_To see complete usage run this command:_

```
python3 men_and_mice_report.py -h
```

## [python-boilerplate.py](https://github.com/wjkw1/python-scripts/blob/main/python-boilerplate.py)
This script includes examples for python libraries argparse, getpass, logging and requests (api calls).

**Usage:**
_To see complete usage run this command:_
```
python3 python-boilerplate.py -h
```


# Python Virtual Environments

Creating your virtual environment
```
cd /path/you/desire
mkdir /path/you/desire/py_virtual_envs
cd py_virtual_envs
pip3 -m venv environment_name
```

Enabling use of your virtual environment
```
source /path/you/desire/py_virtual_envs/environment_name/bin/activate
```

I suggest adding an alias to your **.bash_alias** file to make swapping to it easy. Can change alias to whatever you prefer.
```
alias p-venv-env='source /path/you/desire/py_virtual_envs/py-virtual-env/environment_name/bin/activate'
```
