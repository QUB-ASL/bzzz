# Contributing guidelines

_Version: 0.1.0_


## 1. Working with git

### 1.1. General rules

- The `main` branch is locked and noone can push to it directly
- The main development branch is called `dev`
- All development will take place in branches out of dev
- Do not commit big files
- Avoid committing binary files

### 1.2. Git commits

- Use informative commit messages: "fix stuff" is a bad commit message
- Make several commits as you write code (typically several every day)
- Commits should be _atomic_
- Multi-line git commit messages are encouraged. An example of a good commit message is

```
Change Serial baud rate in ESP to 115200

Addresses #101
```

### 1.3. Versioning

- This project uses [semantic versioning](https://semver.org/)
- When a new version is released, we should create a [tag](https://git-scm.com/book/en/v2/Git-Basics-Tagging)


### 1.4. Branches and pull requests

- Every branch should address a _specific_ issue or development goal
- Branch names should with either of
    - `feature/`
    - `fix/`
    - `dev/`
- To create a new branch do 

```git
git checkout -b feature/1-read-imu` dev
```

- Every branch should be associated with a pull request (PR); after you crate a branch, create a PR
- Pull requests must have an adequately detailed description
- Avoid lengthy PRs with lots of changes
- No PR will be merged to `dev` unless it has been tested (evidence should be provided)
- The branch `dev` will be merged into `main` before making a new release

### 1.5. Issues

- If you have found a bug or you want to request a new feature, create an issue 
- Make sure your bug report is accompanied by a _minimal reproducible example_ (MRE)


## 2. Project structure

ESP32 files:

- `include/` header files (`.h`) 
- `lib/` local libraries
- `src/` C++ source files (`.cpp`)
- `test/` [unit tests](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- `platform.ini` PlatformIO configuration file

Raspberry Pi:
- `raspberry/` any 

Design:
- `design/` any design files (sketches, etc)


## 3. Coding good practice 

### 3.1. C/C++

We follow [this](https://lefticus.gitbooks.io/cpp-best-practices/content/03-Style.html) style guide and naming convention. 
Additionally, make sure you use descriptive variable names, that is, `angular_velocity_rad_s` instead of `w`.

### 3.2. Python

- Just follow [PEP8](https://peps.python.org/pep-0008/)
- Make sure you have read the corresponding [naming convention](https://peps.python.org/pep-0008/#naming-conventions)
- Use virtualenv

### 3.3. Documentation and comments

- Overall, adequate documentation should be provided to allow anyone to construct this quadcopter and contribute to the code
- In C++, the code should be documented using [Doxygen](https://www.doxygen.nl/manual/docblocks.html)-style docstring
- In Python, the code should be documented using [Sphinx](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) docstring

### 3.4. Testing and CI

Guidelines will follow

