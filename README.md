# EQMACEMU_CharacterTransferTool
Python-based Character Transfer Tool to Copy characters from a EQEMU DB to a EQMACEMU DB

## Quickstart
To begin, create a database dump of your eqemu player tables.

Then copy the .env example file that keeps your database secrets.
```bash
$ cp .env.example .env
```
Next update the .env file with your database details. Finally, use the script.
```
$ python migrate_sql.py --help
usage: migrate_sql.py [-h] [-c CHARACTER]

PEQ to TAKP character transfer tool

options:
  -h, --help            show this help message and exit
  -c CHARACTER, --character CHARACTER
```
Copying a character is as easy as the following:
```
$ python migrate_sql.py -c Soandso
```