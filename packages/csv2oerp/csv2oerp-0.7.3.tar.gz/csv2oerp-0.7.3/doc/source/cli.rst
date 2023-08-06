.. _cli:

Command line Interface
**********************

You can call your script in command line to dynamically modify importation params.

To prevent from importing csv file headers, type the following::

    $ ./your_script.py -o1

To import only few lines (First ten's), type the following::

    $ ./your_script.py -l10

For further details::
    
    $ ./your_script --help

Command line options
--------------------

Usage: SCRIPT NAME [options]

Options:
  -h, --help            show this help message and exit
  -f FILENAME, --filename=FILENAME
                        The CSV file to import.
  -s DELIMITER, --separator=DELIMITER
                        The delimiter of the CSV file.
  -g QUOTECHAR, --quotechar=QUOTECHAR
                        The quotechar of the CSV file.
  -e ENCODING, --encoding=ENCODING
                        The encoding of the CSV file.
  -o OFFSET, --offset=OFFSET
                        Offset (Usually used for header omission, default=1)
  -d, --debug           debug mode
  -v, --verbose         verbose mode
  -q, --quiet           don't print anything to stdout
  -l LIMIT, --limit=LIMIT
                        Limit
  -u USERNAME, --username=USERNAME
                        Username
  -p PASSWORD, --password=PASSWORD
                        Password
  -r HOST, --host=HOST  Host to contact
  -t PORT, --port=PORT  Port used
  -b DBNAME, --database=DBNAME
                        Database name

Example of automation
---------------------

Coming soon ...
