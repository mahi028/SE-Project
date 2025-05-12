# SE-Project 

## Overview

Add things here

## How to contribute

1. Fork the Repo

2. Import Repository via git

```bash
git clone repo_name
git branch your_branch_name
git checkout your_branch_name
```

3. Contribute

```bash
git add file_name
```

```bash
git commit -m "commit_msg"
```

```bash
git push orgin your_branch_name
```

> Make sure you only add the files you contributed to. Never use `git add .` to add files.

## How to setup

1. Create and activate virtual environment
```bash
py -m venv env
./env/Scripts/activate
```

For debien/linux

```bash
py -m venv env
source ./env/bin/activate
```

2. Install required dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
py run.py
```

> If running for the first time without database instance (check instance folder)
```bash
py run.py init_db
```


## Things to consider before submitting a pull request

Add things here directory-wise

## Library used

Add things here