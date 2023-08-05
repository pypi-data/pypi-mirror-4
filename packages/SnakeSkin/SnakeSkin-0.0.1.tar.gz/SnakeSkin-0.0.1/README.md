# SnakeSkin

SnakeSkin is a Python package skeleton tool designed to bootstrap new Python
libraries. If you come from the Ruby world, this is built after the `bundle gem`
command in [Bundler](https://github.com/carlhuda/bundler).

# Installation

This is in pip. `pip install snake_skin`

# Usage

SnakeSkin comes with a binary `snake_skin` that handles all the fun.  The main
command in `snake_skin` is `snake_skin shed PROJECT_NAME`.  This will:

* Create `PROJECT_NAME` directory
* Setup barebones PyPI-compliant package conventions (setup.py, package dir, etc)
* Initialize empty git repository
