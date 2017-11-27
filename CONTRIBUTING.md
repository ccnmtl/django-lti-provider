# Contributing

We'd love for you to contribute to our source code! Here are the guidelines we'd like you to follow:

 - [Code of Conduct](#coc)
 - [Issues and Bugs](#issue)
 - [Getting Started](#start)
 - [Coding Rules](#rules)
 - [Making Trivial Changes](#trivial)
 - [Making Changes](#changes)
 - [Submitting Changes](#submit)
 - [Further Info](#info)

## <a name="coc"></a> Code of Conduct
Help us stay open and inclusive by following our [Code of Conduct](https://github.com/ccnmtl/django-lti-provider/blob/master/CODE_OF_CONDUCT.md).

## <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
submitting an issue to our [GitHub issue tracker](https://github.com/ccnmtl/django-lti-provider/issues). Even better you can submit a Pull Request with a fix :heart_eyes:.

**Please see the Submission Guidelines below**.

## <a name="start"></a> Getting Started

* Make sure you have a [GitHub account](https://github.com/signup/free)
* Submit a ticket for your issue, assuming one does not already exist.
  * Clearly describe the issue including steps to reproduce when it is a bug.
  * Make sure you fill in the earliest version that you know has the issue.
* Fork the repository into your account on GitHub

## <a name="rules"></a> Coding Rules
To ensure consistency throughout the source code, please keep these rules in mind as you are working:

* All features or bug fixes **must be tested** by one or more unit tests.
* We follow the conventions contained in:
     * Python's [PEP8 Style Guide](https://www.python.org/dev/peps/pep-0008/) (enforced by [flake8](https://pypi.python.org/pypi/flake8))
     * Javscript's [ESLint](http://eslint.org/) errors and warnings.  
* The master branch is continuously integrated by [Travis-CI](https://travis-ci.org/), and all tests must pass before merging.

## <a name="changes"></a>Making Changes

* Create a topic branch from where you want to base your work.
  * This is usually the master branch.
  * Only target release branches if you are certain your fix must be on that
    branch.
  * To quickly create a topic branch based on master; `git checkout -b
    fix/master/my_contribution master`. Please avoid working directly on the
    `master` branch.
* Create your patch, **including appropriate test cases**.
* Make commits of logical units.
* Run `make` to make sure the code passes all tests.
* Make sure your commit messages are in the proper format.

## <a name="submit"></a>Submitting Changes

* Push your changes to a topic branch in your fork of the repository.
* Submit a pull request to the repository in the ccnmtl organization.
* The core team reviews Pull Requests on a regular basis, and will provide feedback
