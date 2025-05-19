# SE-Project

### Overview

Add things here

### How to contribute

1. Fork the Repo \(Optional\)

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
git push origin your_branch_name
```

> Make sure you only add the files you contributed to. Never use `git add .` to add files.

> Make sure your branch name corresponds to you github username

4. Make a pull request from github

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

> If running for the first time without database instance (check instance folder)
```bash
py run.py init_db
```

4. Check `http://localhost:5000/api` endpoint


### Things to consider before submitting a pull request

Add things here directory-wise

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

#### Run Unit Tests with [Vitest](https://vitest.dev/)

```sh
npm run test:unit
```

#### Run End-to-End Tests with [Cypress](https://www.cypress.io/)

```sh
npm run test:e2e:dev
```

This runs the end-to-end tests against the Vite development server.
It is much faster than the production build.

But it's still recommended to test the production build with `test:e2e` before deploying (e.g. in CI environments):

```sh
npm run build
npm run test:e2e
```

#### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
