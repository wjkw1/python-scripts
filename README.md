# python-scripts
Repo to collate useful example python scripts in one place for future use.

## Python script boilerplate
This script includes examples for python libraries argparse, getpass, logging and requests (api calls). Check it out: [python-boilerplate.py](https://github.com/wjkw1/python-scripts/blob/main/python-boilerplate.py)

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
