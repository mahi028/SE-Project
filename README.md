# SE-Project

### Overview

Add things here

### How to contribute

1. Fork the Repo \(Optional\)

2. Import Repository via git

```bash
git clone https://github.com/mahi028/SE-Project.git
```

> In case of fork, clone your forked repo

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
git push origin your_branch_name
```

> Make sure you only add the files you contributed to. Never use `git add .` to add files.

> Make sure your branch name corresponds to you github username

4. Make a pull request from github

5. Tests 

There are tests in the project. Make sure you run them before submitting a pull request.

After you have pushed your code and created a pull request, make sure all the tests are passing in workflow. Only after all test have passed, your pull request will be merged.

## SE-Project-Backend

### How to setup

1. Create and activate virtual environment
```bash
cd backend
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
py -m pip install --upgrade pip
pip install -r requirements.txt
```

3. Run the application
```bash
py run.py
```

4. Check `http://localhost:5000/graphql` endpoint


### Things to consider before submitting a pull request

Add things here directory-wise
#### Tests
After you have added your code, make sure to add tests for it.
- Only add tests to the tests directory. Do not add any other code to this directory.
- Only push the files after all tests are passing.
- To run tests, run the following command:
```bash
pytest
```


### Library used

Add things here


---

## SE-Project-Frontend

This template should help get you started developing with Vue 3 in Vite.

### Recommended IDE Setup

[VSCode](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) (and disable Vetur).

### Customize configuration

See [Vite Configuration Reference](https://vite.dev/config/).

### Project Setup

```sh
cd frontend
npm install
```

#### Compile and Hot-Reload for Development

```sh
npm run dev
```

#### Compile and Minify for Production

```sh
npm run build
```

#### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```


