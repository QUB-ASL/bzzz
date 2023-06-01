# Contributing guidelines

_Version: 0.1.2_


## 1. Working with git

### 1.1. General rules

- The `main` branch is locked and no-one can push to it directly
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
    - `feature/` for new developments, including documentation
    - `fix/` for bug fixes
    - `hotfix/` for quick fixes (hotfixes should be _very_ small changes)
- To create a new branch do 

```git
git checkout dev
git pull origin dev
git checkout -b feature/123-read-imu dev
```

where the number `123` corresponds to the number of an open issue.

- After you create a branch, create a PR for your code to be reviewed
- When you create a new PR, make sure that the base branch is `dev` (not `main`), unless you want to create a new release (see below)
- Pull requests must have an adequately detailed description
- Avoid lengthy PRs with lots of changes (each PR should focus on one issue)
- No PR will be merged to `dev` unless it has been tested (evidence should be provided)
- The branch `dev` will be merged into `main` before making a new release (`CHANGELOG.md` must be updated when doing so)
- All PRs must be reviewed before they can be merged
- When a PR is ready for review, its author should invite at least one of the collaborators to review it
- Do not merge other people's PRs

**Important:** All invited reviewers should complete their reviews in a timely manner! 


### 1.5. Pull request template

When you create a new PR, you will see the following template:

> ## Main Changes
>
> :warning: Before you make a contribution make sure you've read bzzz's **contributing guidelines**
>
> :warning: Do not make a PR to merge into `main`; merge into `dev` instead (unless you are creating a new release)
>
> Is this a PR about some _specific_ development (e.g., reading values from the IMU)? If not, don't submit it. 
>
> Describe the main changes here
>
>
> ## Associated Issues
>
> - Closes #1
> - Addresses #2


You need to **modify it**. 


### 1.6. Issues

- If you have found a bug, or you want to request a new feature, create an issue 
- Make sure your bug report is accompanied by a _minimal reproducible example_ (MRE)
- When you create an issue, assign it to someone (e.g., yourself)
- Use appropriate labels for your issues


## 2. Project structure

ESP32 files:

- `include/` header files (`.h`) 
- `lib/` local libraries
- `src/` C++ source files (`.cpp`)
- `test/` [unit tests](https://docs.platformio.org/en/latest/advanced/unit-testing/index.html)
- `platform.ini` PlatformIO configuration file
- `hardware/tests/` Various "manual" tests for our components (e.g., IMU/AHRS, motors, radio, etc)

Raspberry Pi:
- `raspberry/` any 

Design:
- `design/` any design files (sketches, etc)


## 3. Coding good practice 

### 3.1. C/C++

Bzzz's C++ naming convention is as follows:

- Make sure you use descriptive variable names, that is, `angularVelocity` instead of `w`
- Class and structure names are PascalCase (camel case with first letter uppercase); in most other cases we use camel case as this is the standard in the community
- Preprocessor directives are in "screaming snake case", e.g., `DEBUG_MODE` or `FRONT_LEFT_ESC_PIN`
- Global constants use the prefix `c_`, e.g., `c_controllerGain`
- Private class members use the prefix `m_`, e.g., `m_privateVariable`
- Global variables use the prefix `g_`, e.g., `g_imuData`
- When it comes to getters and setters we use `foo()` (_not_ `getFoo()`) and `setFoo(val)`
- All other variables (e.g., local variables) are camel case
- The main namespace of the project is `bzzz`

**What goes in a header file:** Declare all public entities. Is a function/method/class/structure needed outside the scope of this file? If not, it does not belong in the header file. Do not put any implementations in the header file - put them in the code files instead. For example, is the controller gain needed to anyone else except for the controller? No, so put it in the `cpp` file.

### 3.2. Python

- Just follow [PEP8](https://peps.python.org/pep-0008/)
- Make sure you have read the corresponding [naming convention](https://peps.python.org/pep-0008/#naming-conventions)
- Use `virtualenv` to run your Python code

<details>
  <summary>Python tips</summary>

  - Study [PEP8](https://peps.python.org/pep-0008/) carefully (and follow it)
  - Classes are `CamelCase`
  - Function/method names are `snake_case`
  - Use an autopep8 formatter in VS code
  - Unused (output) variables are `_like_this`
  - Avoid one-letter or confusing variable names (e.g., use `acceleration` instead of `a`)
  - Should this method be public? Think again! If not, make it a `__private_method()`

</details>

### 3.3. Documentation and comments

- Overall, adequate documentation should be provided to allow anyone to construct this quadcopter and contribute to the code
- In C++, the code should be documented using [Doxygen](https://www.doxygen.nl/manual/docblocks.html)-style docstrings
- In Python, the code should be documented using [Sphinx](https://sphinx-rtd-tutorial.readthedocs.io/en/latest/docstrings.html) docstrings

Example of C++ documentation:

```c++
/**
 * @brief computes control action
 *
 * @param systemState state of the system
 *
 * @return control voltage
 */
float controlAction(float systemState);
```

### 3.4. Testing and CI

- Testing is done using unity
- Test source files are in `test/`; you can find examples there
- To run the tests click on "test" in the top right corner of VS Code or run `pio test` in the PlatformIO client
- Contrary to the rest of the code, the test functions are snake case (not camel case) and use the prefix `test_`


## 4. ESP32-specific details

### 4.1. Timer interrupts and volatile variables

When an interrupt routine accesses a global variable (read/write), it should be declared using the `volatile` keyword. For example

```c++
hw_timer_t *ledTimer = nullptr;
volatile bool ledStatus = false;

/**
 * Timer interrupt function
 */
void IRAM_ATTR onTimer()
{
  ledStatus = !ledStatus;
}
```

If we omit the `volatile` keyword, the compiler may drop the variable `ledStatus`.

### 4.2. Memory shared between ISR and `loop()`

If a variable is shared between a timer interrupt and the loop, we need to account for the **critical sections** of the code.

```c++
portMUX_TYPE timerMux = portMUX_INITIALIZER_UNLOCKED;

/**
 * Timer interrupt function 
 */
void IRAM_ATTR onTimer()
{
  // guard the section where we need to read/write `ledStatus`
  // using `timerMux`
  taskENTER_CRITICAL_ISR(&timerMux);
  ledStatus = !ledStatus;
  taskEXIT_CRITICAL_ISR(&timerMux);
}

/**
 * Loop function
 */
void loop()
{
  // enter and exit a critical section in the loop too
  taskENTER_CRITICAL_ISR(&timerMux);
  digitalWrite(LED_PIN, ledStatus);
  taskEXIT_CRITICAL_ISR(&timerMux);
}
```


# 5. Electronics

The sketches and grb files should be part of this project.