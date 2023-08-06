# -*- coding: utf8 -*-
################################################################################
#
# Copyright (c) 2012 STEPHANE MANGIN. (http://le-spleen.net) All Rights Reserved
#                    Stéphane MANGIN <stephane.mangin@freesbee.fr>
# Copyright (c) 2012 OSIELL SARL. (http://osiell.com) All Rights Reserved
#                    Eric Flaux <contact@osiell.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
################################################################################

"""

`csv` declaration
^^^^^^^^^^^^^^^^^

"""
import os
import sys
import xmlrpclib
import logging
import time
import logging.handlers
import inspect
from copy import copy
from copy import deepcopy
from optparse import OptionParser
from pprint import pformat
try:
    import progressbar
    from progressbar import ETA
    from progressbar import FileTransferSpeed
    from progressbar import Percentage
    from progressbar import ProgressBar
    from progressbar import SimpleProgress
except ImportError:
    progressbar = None

from csv2oerp import exceptions
from csv2oerp import tools
from csv2oerp.constants_and_vars import STATS, FORMAT
from csv2oerp.lib import unicode_csv


class Session(object):
    """Main class which provides the functionnal part of the importation process.

    .. note:: `sys.argv` integrated provides a command line parser.

    Here are the available command line arguments::

        -h, --help                  Show this kind of help message and exit
        -o OFFSET, --offset=OFFSET  Offset (Usually for header omission)
        -l LIMIT, --limit=LIMIT     Limit
        -c, --check-mapping         Check mapping template
        -v, --verbose               Verbose mode
        -d, --debug
           debug mode
        -q, --quiet                 Doesn't print anything to stdout

    """
    __slots__ = [
        u'_syslog_mode', u'_columns_mapping', u'_processed_lines', u'_uid',
        u'_preconfigure', u'_current_mapping', u'_encoding', u'_logger', u'_opts',
        u'_hdlr', u'_lang', u'id', u'name', u'filename', u'delimiter', u'quotechar',
        u'encoding', u'offset', u'limit', u'server', u'models',
    ]

    @property
    def lines(self):
        """Getting all lines from CSV parser.

        :returns: list

        """
        return deepcopy(list(self._lines()))

    def __init__(self, name, filename, delimiter=u';', quotechar=u'"',
                 encoding=u'utf-8', offset=0, limit=None, quiet=False, debug=False,
                 **kwargs):

        # Unique id of this import
        self.name = unicode(name)
        self.id = unicode(time.time())

        # Pass args to sys.argv
        self._syslog_mode = False
        self._columns_mapping = {}
        self._processed_lines = None
        self._uid = None
        self._preconfigure = None
        self._current_mapping = None
        self._encoding = u'utf-8'
        self._logger = None

        parser = OptionParser()
        parser.add_option(u"-f", u"--filename",
                          action=u"store",
                          dest=u"filename",
                          default=filename,
                          help=u"The CSV file to import.")
        parser.add_option(u"-s", u"--separator",
                          action=u"store",
                          dest=u"delimiter",
                          default=delimiter,
                          help=u"The delimiter of the CSV file.")
        parser.add_option(u"-g", u"--quotechar",
                          action=u"store",
                          dest=u"quotechar",
                          default=quotechar,
                          help=u"The quotechar of the CSV file.")
        parser.add_option(u"-e", u"--encoding",
                          action=u"store",
                          dest=u"encoding",
                          default=encoding,
                          help=u"The encoding of the CSV file.")
        parser.add_option(u"-o", u"--offset",
                          action=u"store",
                          type=u"int",
                          dest=u"offset",
                          default=offset,
                          help=u"Offset (Usually used for header omission, default=1)")
        parser.add_option(u"-d", u"--debug",
                          action=u"store_true",
                          dest=u"debug",
                          default=False,
                          help=u"debug mode")
        parser.add_option(u"-v", u"--verbose",
                          action=u"store_true",
                          dest=u"verbose",
                          default=debug,
                          help=u"verbose mode")
        parser.add_option(u"-q", u"--quiet",
                          action=u"store_true",
                          dest=u"quiet",
                          default=quiet,
                          help=u"don't print anything to stdout")
        parser.add_option(u"-l", u"--limit",
                          action=u"store",
                          dest=u"limit",
                          type=u"int",
                          default=limit,
                          help=u"Limit")
        # Connection options
        parser.add_option(u"-u", u"--username",
                          action=u"store",
                          dest=u"username",
                          default=u'admin',
                          help=u"Username")
        parser.add_option(u"-p", u"--password",
                          action=u"store",
                          dest=u"password",
                          default=u'admin',
                          help=u"Password")
        parser.add_option(u"-r", u"--host",
                          action=u"store",
                          dest=u"host",
                          default=u'localhost',
                          help=u"Host to contact")
        parser.add_option(u"-t", u"--port",
                          action=u"store",
                          dest=u"port",
                          default=8069,
                          help=u"Port used")
        parser.add_option(u"-b", u"--database",
                          action=u"store",
                          dest=u"dbname",
                          default=u'test',
                          help=u"Database name")
        (self._opts, args) = parser.parse_args()
        self.filename = self._opts.filename
        self.delimiter = self._opts.delimiter
        self.quotechar = self._opts.quotechar
        self.encoding = self._opts.encoding
        self.offset = self._opts.offset
        self.limit = self._opts.limit
        self.models = []
        self.server = None

        # Global statistics
        STATS[self.id] = {
            u'importfile': self.filename,
            u'actual_line': [],
            u'col_num': 0,
            u'line_num': 0,
            u'errors': 0,
            u'warnings': 0,
            u'line_skipped': 0,
            u'line_done': 0,
            u'object_skipped': 0,
            u'object_created': 0,
            u'object_written': 0
        }
        # Initialize logger
        if not self._logger:
            self.set_logger()
            self._logger.info(
                u"Logger set to '%s'" % self.name, extra=STATS[self.id])

    def _lines(self):
        """Reader a line generator from self.filename. Apply offset and limit
        restriction.

        .. versionadded: 0.6

        .. note: Call th preconfigure script and execute if any.

        """
        if self.filename is None:
            raise Exception(u"File to import has not been set !")

        # Getting lines to import
        ucsv = unicode_csv.Reader(
            self.filename, delimiter=self.delimiter, quotechar=self.quotechar)
        self._processed_lines = tools.clean_lines(ucsv)
        self._logger.info(u"Lines: %s" % int(len(self._processed_lines)),
                          extra=STATS[self.id])

        # Applying `offset` limitation
        if self.offset:
            if STATS[self.id][u'line_skipped'] < self.offset:
                # Bug d'affchage des lignes skippée
                STATS[self.id][u'line_skipped'] += self.offset
            self._logger.info(
                u"Offset: %s" % self.offset, extra=STATS[self.id])

        # Applying `limit` limitation
        self._logger.info(u"Limit: %s" % self.limit, extra=STATS[self.id])

        filename_called = os.path.split(inspect.stack()[2][1])[-1]
        if self._preconfigure and self._preconfigure != filename_called:
            script_to_import, script_extention = os.path.splitext(
                self._preconfigure)
            if script_extention == u'.py':
                self._logger.info(
                    u"Calling preconfigure script", extra=STATS[self.id])
                self._processed_lines = __import__(script_to_import).main(self)

        # Init line incrementor
        STATS[self.id][u'line_num'] = self.offset

        # LINE ITERATION
        #===============================================================
        return self._processed_lines

    def __str__(self):
        return u"<Session %s:%s (%s)>" % (self.server.host, self.server.db, self._lang)

    def start(self):
        """Start the importation process

        """
        # Finally launch the import
        return self._launch_import()

    #===========================================================================
    # Accessors
    #===========================================================================
    def set_mapping(self, mapping):
        """ Columns mapping configuration.

        See ``Creation of your Columns mapping`` for further details.

        """
        STATS[self.id][u'importfile'] = self.filename
        self._current_mapping = mapping

    def set_lang(self, code=u'en_EN'):
        """ Set current lang

        :param code: The standardized code of a language
        :type code: str

        """
        self._lang = code

    def set_logger(self, verbose=False, debug=False, quiet=False, syslog=False):
        """ Configure and initialize the logger facility.

        .. note:: Optionnal

        :param name: Name of the logger (name of import session is used if None)
        :type name: str
        :returns: bool

        """
        global STATS, FORMAT
        logfile = os.path.join(self.name + u".log")
        buff = open(logfile, u'w')
        buff.close()
        self._logger = logging.getLogger(self.name)
        if syslog:
            self._hdlr = logging.handlers.SysLogHandler(
                address=self._syslog_mode,
                facility=logging.handlers.SysLogHandler.LOG_USER
            )
        else:
            self._hdlr = logging.FileHandler(logfile)

        # Format du logger
        STATS[self.id][u'importfile'] = self.filename
        formatter = logging.Formatter(FORMAT)
        self._hdlr.setFormatter(formatter)
        self._logger.addHandler(self._hdlr)

        if not self._opts.quiet or quiet:
            # In all times, show WARNING and ERROR messages
            logging.basicConfig(format=FORMAT)
            self._logger.setLevel(logging.WARNING)

            if self._opts.verbose or verbose:
                self._logger.setLevel(logging.INFO)

            if self._opts.debug or debug:
                self._logger.setLevel(logging.DEBUG)

        return True

    def _name_get(self, model, id_=False, data={}):
        if not id_ and data:
            return u'name' in data and unicode(data[u'name'])\
                or u'nom' in data and unicode(data[u'nom'])\
                or u'surname' in data and unicode(data[u'surname'])\
                or u'prenom' in data and unicode(data[u'prenom'])\
                or u'state' in data and unicode(data[u'state'])\
                or u'etat' in data and unicode(data[u'etat'])\
                or u'value' in data and unicode(data[u'value'])\
                or u'valeur' in data and unicode(data[u'valeur'])\
                or u'id' in data and unicode(data[u'id'])\
                or unicode(data.itervalues().next())
        elif id_:
            try:
                return unicode(self.server.name_get(model, id_))
            except:
                pass
        return u"NONAME"

    def set_preconfigure_script(self, filename):
        """ Declare a parrallel script which will be called before importation.

        It must implement a main method which take in params the instance of
        Import class, it will be able to use all facilities from Import class.

        It must return a list of lines (lines already list too)

        """
        self._preconfigure = filename

    #===========================================================================
    # Tools
    #===========================================================================
    def get_line_from_index(self, line_num):
        """ Retrieve lines which have value at column

        :param line_num: The index of line
        :type line_num: value
        :returns: tuple

        """
        i = 1
        for line in self.lines:
            if i == int(line_num):
                return line
            i += 1
        raise IndexError

    def get_lines_from_value(self, column, value):
        """ Retrieve lines which have value at column

        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: tuple

        """
        res = []
        for line in self.lines:
            value_type = type(line[column])
            value = value_type(value) or value
            if line[column] == value:
                res.append(line)
        return res

    def get_index_from_value(self, column, value, withcast=True):
        """ Retrieve lines which have ``value`` at ``column``

        By default ``value`` will be casted by ``column`` value type
        overwrite it by withcast=False

        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: int

        """
        res = []
        index = 0
        for line in self.lines:
            value_type = type(line[column])
            value = withcast and value_type(value) or value
            if line[column] == value:
                res.append(index)
            index += 1
        return res

    #===========================================================================
    # Search and Get methods
    #===========================================================================
    def search(self, model, data):
        """Search in `OpenERP` if a ``model`` contains a records which matched all
        field in ``data``

        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of field used to search for an existing object
        :type search: list
        :returns: int

        """
        global STATS
        STATS[self.id][u'importfile'] = self.filename

        res = []
        list_search = []
        self._logger.debug(u'<%-25s> search:%s' % (model.name, model.search),
                           extra=STATS[self.id])

        for item in model.search:
            if item in data.keys():
                list_search.append((item, u'=', data[item]))

        self._logger.debug(
            u'<%-25s> list_search:%s' % (model.name, list_search),
            extra=STATS[self.id])

        for (item, sign, val) in copy(list_search):
            if val in (u"", u" ", None):
                list_search = []
                break

        if list_search:
            res = self.server.search(model.name, list_search, 0, False,
                                     False, {u'lang': self._lang})
            self._logger.debug(u'<%-25s> search result %s' % (model.name, res),
                               extra=STATS[self.id])

        return res

    #===========================================================================
    # Creation methods
    #===========================================================================
    def create(self, model, data):
        """Effective object creation process within ``model`` and ``data`` values
        Search for a previous object before creation within search param.

        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of field used to search for an existing object
        :type search: list
        :returns: int

        """
        global STATS
        STATS[self.id][u'importfile'] = self.filename
        _id = False
        error = None
        state = u'old'

        # Manage null values
        for attr, value in data.items():
            try:
                data[attr] = value.strip(u' \t\n\r\r\n')
            except:
                pass
            if data[attr] in ('', None):
                del data[attr]

        self._logger.debug(u'<%-25s> data:%s' % (model.name, data),
                           extra=STATS[self.id])

        # If data is empty SKIPPED
        if not data:
            self._logger.warning(u"<%-25s> Null values" % model.name,
                                 extra=STATS[self.id])
            STATS[u'objects'][model.name][u'skipped'] += 1

        else:
            try:

                if u'id' in data and data[u'id']:
                    _id = int(data[u'id'])
                    del data[u'id']
                else:
                    _id = self.search(model, data)
                    _id = _id and _id[0] or False

                name = tools.strip_accents(self._name_get(model, data=data))

                if not _id:
                    state = u"new"
                    if model.create:
                        _id = self.server.create(
                            model.name, data, context={u'lang': self._lang})
                        self._logger.info(
                            u"<%-25s> CREATE [%s]" % (model.name, _id),
                            extra=STATS[self.id])
                        STATS[self.id][u'object_created'] += 1
                        STATS[u'objects'][model.name][u'created'] += 1
                    else:
                        self._logger.info(
                            u"<%-25s> NO CREATE [%s]" % (
                                model.name, _id or name),
                            extra=STATS[self.id])

                else:
                    state = u'old'
                    if model.update:
                        self.server.write(model.name, [_id], data)
                        self._logger.info(
                            u"<%-25s> UPDATE [%s]" % (model.name, _id),
                            extra=STATS[self.id])
                        STATS[self.id][u'object_written'] += 1
                        STATS[u'objects'][model.name][u'written'] += 1
                    else:
                        self._logger.info(
                            u"<%-25s> NO UPDATE [%s]" % (model.name, _id),
                            extra=STATS[self.id])

            except xmlrpclib.Fault as err:
                try:
                    error = unicode(err.faultString.split(u'\n')[-2])
                except:
                    error = unicode(err.faultString + (err.faultCode or u''))\
                        or u'Unknown error (xmlrplib.Fault)'
            except Exception as err:
                error = unicode(err) or u'Unknown error (Exception)'

        if error:
            _id = False
            state = u'none'
            error = error.replace(u'\\n', u'\n').replace(u'\\', u'')
            try:
                self._logger.error(u"<%-25s> id:%s %s" %
                                   (model.name, _id, error), extra=STATS[self.id])
                self._logger.debug(u"<%-25s> id:%s|state:%s|%s" %
                                   (model.name, _id, state, pformat(data)), extra=STATS[self.id])
            except:
                print u'Erreur OPENERP :: %s' % error
            STATS[self.id][u'warnings'] += 1
            STATS[u'objects'][model.name][u'skipped'] += 1
            STATS[u'objects'][model.name][u'error'] += 1

        return _id

    #===========================================================================
    # Column's value retreiver and process launcher
    #===========================================================================
    def _register_model(self, model):
        """ Keeping objects actions to stats further

        .. versionadded: 0.6

        """
        if model.name not in STATS[u'objects']:
            STATS[u'objects'][model.name] = {
                u'name': model.name,
                u'written': 0,
                u'created': 0,
                u'skipped': 0,
                u'error': 0,
            }

    def _parse_models(self, line):
        """Start model importation.

        Exceptions checks::

            RequiredFieldError, SkipObjectException, SkipLineException, ColumnIndexError

        """
        for model in self.models:

            state = u'Unknown'
            search = u'Unknown'
            try:

                data = model.get_data(self, line)
                self.create(model, data)
                model.reinit()

            except exceptions.RequiredFieldError as error:
                # Required field not found
                continue

            except exceptions.SkipObjectException as error:
                self._logger.info(u"<%-20s> Object skipped" %
                                  model.name, extra=STATS[self.id])
                STATS[u'objects'][model.name][u'skipped'] += 1
                STATS[self.id][u'object_skipped'] += 1
                # Next object
                continue

            except exceptions.SkipLineException as error:
                self._logger.info(u"<%-20s> Line skipped(%s)" %
                                  (model.name, error), extra=STATS[self.id])
                STATS[self.id][u'line_skipped'] += 1
                # Next line
                break

            except exceptions.ColumnIndexError as error:
                STATS[self.id][u'errors'] += 1
                raise exceptions.FatalException(error, line, model.name, state, search, data, self.lines[line][1:])

            #except Exception as error:
            #    STATS[self.id][u'errors'] += 1
            #    raise exceptions.FatalException(error, line, model.name, state, search, data, self.lines[line][1:])

            # Keep line incrementation
            STATS[self.id][u'line_done'] = STATS[self.id][u'line_num']
            # END OBJECTS ITERATION
            #===========================================================
            #self._logger.info(u"next line", extra=STATS[self.id])

    def _launch_import(self, *args, **kwargs):
        """Main function that launch the importation process

        """
        global STATS
        exit = False
        STATS[self.id][u'importfile'] = self.filename
        if not self._opts.quiet:
            sys.stdout.write(u'\n')
            sys.stdout.write(u'*' * 79 + u'\n')
            sys.stdout.write(u'* %s\n' % self.name)

        # Register models on global statistics
        for model in self.models:
            self._register_model(model)
            for mod in model.get_relationnal_models():
                self._register_model(mod)

        #=======================================================================
        # Open file, call preconfigure if given in arg
        #=======================================================================
        try:
            if progressbar and not self._opts.quiet and not self._opts.verbose:
                pbar = ProgressBar(widgets=[u'Processing line ', SimpleProgress(), u' (', Percentage(), u' | ', ETA(), u' | ', FileTransferSpeed(), u')'], maxval=len(self.lines) + 1).start()
            for line in self.lines[self.offset:self.limit]:
                # Keeping stats
                STATS[self.id][u'line_num'] += 1
                STATS[self.id][u'actual_line'] = line

                # Instanciate a dictionnary which will receive values
                # from CSV line according to columns mapping
                self._parse_models(line)

                if progressbar and not self._opts.quiet and not self._opts.verbose:
                    pbar.update(int(STATS[self.id][u'line_num']))

                # Flush models
                for model in self.models:
                    model.reinit()

            if progressbar and not self._opts.quiet and not self._opts.verbose:
                pbar.finish()

            self._logger.info(u"END import", extra=STATS[self.id])

        except exceptions.FatalException as error:
            print error
            exit = True

        except KeyboardInterrupt:
            self._logger.error(u'CTRL^C caught !', extra=STATS[self.id])
            exit = True

        finally:
            if not self._opts.quiet:
                sys.stdout.write(u'*' * 79 + u'\n')
                sys.stdout.write(u'Object Skipped %(object_skipped)11s' %
                                 STATS[self.id])
                sys.stdout.write(u' | Line Skipped %(line_skipped)11s' %
                                 STATS[self.id])
                sys.stdout.write(u' | Total Errors %(errors)10s' %
                                 STATS[self.id])
                sys.stdout.write(u'\n')
                sys.stdout.write(u'Object Created %(object_created)11s' %
                                 STATS[self.id])
                sys.stdout.write(u' | Line Done    %(line_done)11s' %
                                 STATS[self.id])
                sys.stdout.write(u' | Total Warnings%(warnings)9s' %
                                 STATS[self.id])
                sys.stdout.write(u'\n')
                sys.stdout.write(u'Object Written %(object_written)11s' %
                                 STATS[self.id])
                sys.stdout.write(u'\n')

            STATS[self.id] = {
                u'importfile': None,
                u'actual_line': [],
                u'line_num': 0,
                u'col_num': 0,
                u'errors': 0,
                u'warnings': 0,
                u'line_skipped': 0,
                u'line_done': 0,
                u'object_skipped': 0,
                u'object_created': 0,
                u'object_written': 0,
            }

            if exit:
                del self
                sys.exit(1)

        return True

    #===========================================================================
    # Public methods
    #===========================================================================
    def log(self, level, model=None, msg="", line=None):
        """Allow to use the internal logger to log special message outside of
        the importation process.

        """
        global STATS
        STATS[self.id][u'importfile'] = self.filename
        if level not in (u'debug', u'info', u'warning', u'error'):
            raise Exception(u"logger, invalid level")
        old_line = STATS[self.id][u'line_num']
        if line:
            STATS[self.id][u'line_num'] = line
        if not self._logger:
            self.set_logger()
        getattr(self._logger, level)(u"%s%s" % (model and u'<%-25s> ' %
                                                model.name or u'', msg), extra=STATS[self.id])
        STATS[self.id][u'line_num'] = old_line

    @staticmethod
    def _check_server(server):
        """Check if the server is valid.

        """
        if 'Openerp' != server.__class__.__name__:
            raise Exception(u"Server must inherit from csv2oerp.models.connector.Openerp.")
        return True

    def bind(self, server=None, models=[]):
        """Associate server and models, and launch importation.

        :param server: The server to bind to
        :type server: :class:`csv2oerp.Openerp`
        :param models: List of :class:`csv2oerp.Model` to import
        :returns: bool

        """
        global STATS
        if server is None:
            server = Openerp(self._opts.host, self._opts.port,
                             self._opts.username, self._opts.password,
                             self._opts.dbname)
        self.server = server
        self._lang = server.lang
        self._check_server(server)

        for model in models:
            if hasattr(model, u'iteritems'):
                for key, model in model.iteritems():
                    model.check(self)
                    self.models.append(model)
            else:
                model.check(self)
                self.models.append(model)
            for mod in model.get_relationnal_models():
                mod.check(self)

        return self._launch_import()
