# EZCare

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

4. Make a pull request from github

5. Tests 

There are tests in the project. Make sure you run them before submitting a pull request.

After you have pushed your code and created a pull request, make sure all the tests are passing in workflow. Only after all test have passed, your pull request will be merged.

> For production setup, checkout to prod branch and see README.md there

## EZCare Backend

This backend application currently **only supports Linux environments**.

## Prerequisites

Before running the backend application, you need to install the following dependencies:

```sh
sudo apt install cmake
python3 -m pip install --upgrade pip setuptools wheel
```

## Setup and Installation

1. Unzip and Navigate to the backend directory:
```sh
cd backend
```

2. Create and Activate Virtual Environment (Optional):
```sh
python3 -m venv env
source env/bin/activate
```

3. Install Python dependencies:
```sh
pip install -r requirements.txt
```

## Running the Application

To start the backend server:

```sh
python3 run.py
```

## Running the Application Tests

To start the backend server:

```sh
pytest tests
```

## Running Specific Test modules

To start the backend server:

```sh
pytest tests/{module_name}
```

## Environment Requirements

- **Operating System**: Linux (Ubuntu/Debian recommended)
- **Python**: 3.7 or higher
- **CMake**: Required for certain Python packages

## Notes

- Make sure all prerequisites are installed before attempting to run the application
- The application may not work properly on Windows or macOS due to Linux-specific dependencies
- If you encounter any installation issues, ensure your system is up to date: `sudo apt update && sudo apt upgrade`


---

## EZCare Frontend

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

---

## 📝 License & Support

This project is exclusively built as a pre-requisite for Software Engineering Course for IIT-Madras by Team 6 | May'2025. For support or questions, please refer to the project documentation or create an issue in the repository.

---

## 👥 Contributors

| Name | Role in Project | Roll Number |
|------|-----------------|-------------|
| **Mohit Tewari** | Frontend, Backend, API Integration, Project Design, Code Documentation | 23f1002364 |
| **Akhileshwer Pandey** | Project Manager, Backend, Testing | 21f3002866 |
| **Dev Gupta** | Backend, Project Documentation | 22f2000888 |
| **Rashi Singal** | Frontend, Project Documentation | 21f1005286 |
| **Affan Bin Nishat** | Testing | 21f1003441 |
| **Ajay Sharma** | Frontend | 21f1005414 |
| **Ambuj Pratap** | Frontend | 22f3002778 |

---

**Last Updated**: August 10, 2025  
**Version**: 1.0.0  
**Maintainer**: EZCare Development Team
