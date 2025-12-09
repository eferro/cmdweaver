# cmdweaver

![Python versions supported](https://img.shields.io/badge/supports%20python-3.9%20|%203.10%20|%203.11%20|%203.12-blue.svg)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**cmdweaver** is the base infrastructure to create *ad hoc* shells or command line interfaces using Python.

It includes an engine for command completion, types verification, command help and other useful features. It can be used with readline to provide advanced line editing, history and autocompletion.

## About this Fork

This project is a fork of [aleasoluciones/boscli](https://github.com/aleasoluciones/boscli). While we acknowledge and appreciate the original work, this fork will follow its own direction with different goals and development priorities.

## Examples

See [examples](examples) dir for a minimal ad hoc shell using readline.

## Installation

You can install the package in development mode:

```bash
python -m pip install -e .
```

## Specs

To run the cmdweaver specs you should create a virtual environment, install the development requirements and then run `mamba`.

```bash
python -m pip install -r requirements-dev.txt
mamba
```

## Contribute

If you'd like to contribute, fork this repository and send a pull request.
