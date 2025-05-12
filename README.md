# SE-Project 

## Overview

Add things here

## How to contribute

1. Fork the Repo

2. Import Repository via git

```bash
git clone https://github.com/mahi028/SE-Project.git
```

3. Contribute

```bash
git branch your_branch_name
git checkout your_branch_name
git add file_name
```

```bash
git commit -m "commit_msg"
```

```bash
git push orgin your_branch_name
```

> Make sure you only add the files you contributed to. Never use `git add .` to add files.

4. Make a pull request from github

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

4. Check `http://localhost:5000/api` endpoint


## Things to consider before submitting a pull request

Add things here directory-wise

## Library used

Add things here