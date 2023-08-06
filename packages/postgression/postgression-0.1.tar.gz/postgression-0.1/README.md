# python-postgression

A python client for the postgression API.


## What is This?

This is a simple CLI app that talks to the
[postgression](http://www.postgression.com/) public API, and generates a
temporary PostgreSQL database for usage in your test code (or just general
messing around).

postgression databases are automatically deleted after 30 minutes. No
information is logged by the service.


## Installation

You can install ``postgression`` using
[pip](http://pip.readthedocs.org/en/latest/):

``` bash
$ pip install postgression
```


## Usage

Once you've got ``postgression`` installed, you can generate a new PostgreSQL
database by running ``postgression``... like so:

``` bash
$ postgression
postgres://user:password@host:port/db
```

Each time you run ``postgression``, you'll get a new PostgreSQL database
provisioned for usage.

If for some reason a database can't be provisioned, an error will be returned.
