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
csv2oerp Access Programming Interface v0.7.

"""
import api07
import models
from copy import deepcopy, copy
from inspect import stack, getargvalues
from constants_and_vars import STATS

ACTION_PATTERN = {
    'skip': 'SKIP',
    'replace': 'REPLACE',
    'ignore': 'IGNORE',
    'noupdate': 'NO_UPDATE',
    'nocreate': 'NO_CREATE',
    'unique': 'UNIQUE',
    'required': 'REQUIRED',
    'router': 'ROUTER',
    }


SERVER = None

def connect(*args, **kwargs):
    """Set globals constants needed to initialize a connection to openerp

    .. versionadded:: 0.5.3

    :param host: IP or DNS name of the OERP server
    :type host: str
    :param port: Port number to reach
    :type port: int
    :param user: Username in the OERP server
    :type user: str
    :param pwd: Password of the username
    :type pwd: str
    :param dbname: Name of the database to reach
    :type dbname: str
    :raises: nothing

    """
    global SERVER
    SERVER = models.connector.Openerp(*args, **kwargs)


class Import_session(object):
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
        '_syslog_mode', '_columns_mapping', '_processed_lines', '_uid',
        '_preconfigure', '_relationnal_prefix', '_current_mapping', '_encoding',
        '_logger', '_opts', '_hdlr', '_lang',
        'id', 'name', 'filename', 'delimiter', 'quotechar', 'encoding', 'offset',
        'limit', 'models', 'kw', 'quiet', 'debug', '_session'
        ]

    def __init__(self, **kw):
        self.offset = 'offset' in kw and kw['offset']
        self.limit = 'limit' in kw and kw['limit']
        self.quiet = 'quiet' in kw and kw['quiet']
        self.debug = 'debug' in kw and kw['debug']
        self.kw = kw
        self._relationnal_prefix = 'REL_'
        self._columns_mapping = {}
        self._current_mapping = None
        self._session = None
        
    #===========================================================================
    # Accessors
    #===========================================================================
    @property
    def server(self):
        """ Return the current socket connection to the OpenERP server (xmlrpc).

        """
        return SERVER

    @property
    def host(self):
        """ Return the current connection host for this session.

        """
        return SERVER.host

    @property
    def port(self):
        """ Return the current connection port for this session.

        """
        return SERVER.port

    @property
    def db(self):
        """ Return the current database name for this session.

        """
        return SERVER.db

    @property
    def user(self):
        """ Return the current username for this session.

        """
        return SERVER.user

    @property
    def uid(self):
        """ Return the current UID for this session.

        """
        return SERVER.uid

    @property
    def pwd(self):
        """ Return the current password for this session.

        """
        return SERVER.pwd
    
    @property
    def lines(self):
        """Getting all lines from CSV parser.
        
        :returns: list

        """
        self._session.lines()

    @property
    def mapping(self):
        """Getting columns mapping configuration.

        """
        return self._columns_mapping

    @property
    def lang(self):
        """Getting current language.

        """
        return SERVER.lang

    def set_mapping(self, mapping):
        """ Columns mapping configuration.

        See ``Creation of your Columns mapping`` for further details.
        
        """
        self._current_mapping = mapping

    def set_lang(self, code='fr_FR'):
        return super(Import_session, self).set_lang(code)
    
    def set_logger(self, syslog=False):
        return super(Import_session, self).set_logger(syslog)

    def set_input_file(self, filename, delimiter=',', quotechar='"',
            encoding='utf8'):
        """ Set the CSV file to use.
        
        """
        self._session = models.Session(filename,
                filename, delimiter, quotechar, encoding,
                offset=self.offset, limit=self.limit,
                quiet=self.quiet, debug=self.debug,
                **self.kw)

    #===========================================================================
    # Tools
    #===========================================================================
    def get_line_from_index(self, line_num):
        """ Retrieve lines which have value at column

        :param line_num: The index of line
        :type line_num: value
        :returns: tuple

        """
        return self._session.get_line_from_index(line_num)
    
    def get_lines_from_value(self, column, value):
        """ Retrieve lines which have value at column

        :param column: The column index
        :type column: int
        :param value: The value to compare from
        :type value: value
        :returns: tuple

        """
        return self._session.get_lines_from_value(column, value)
    
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
        return self._session.get_index_from_value(column, value,
                withcast)
    
    #===========================================================================
    # Public methods
    #===========================================================================
    def log(self, level, msg, line=None, model=None):
        return self._session.log(level, msg, line, model)

    def connect(self, *args, **kwargs):
        """Set constants needed to initialize a connection to OpenERP.

        :param host: IP or DNS name of the OERP server
        :type host: str
        :param port: Port number to reach
        :type port: int
        :param user: Username in the OERP server
        :type user: str
        :param pwd: Password of the username
        :type pwd: str
        :param dbname: Name of the database to reach
        :type dbname: str

        """
        global SERVER
        SERVER = models.connector.Openerp(*args, **kwargs)

    #===========================================================================
    # MiddleWare api06 to api07
    #===========================================================================
    def set_syslog(self, arg=True):
        """ Set if syslog must be used instead of a log file.

        """
        return self._session.set_syslog(arg)

    def set_preconfigure_script(self, filename):
        """ Declare a parrallel script which will be called before importation.

        It must implement a main method which take in params the instance of 
        Import class, it will be able to use all facilities from Import class.

        It must return a list of lines (lines already list too)

        """
        return self._session.set_preconfigure_script(filename)


    def check_mapping(self):
        """Check mapping for semantics errors.
        http://www.openerp.com/forum/topic31343.html
        Also check for required and readonly fields.

        """
        mapping = deepcopy(self._current_mapping)
        title = "Errors occured during mapping check :\n___________________\n\n"
        res = ""
        # Mapping must be iterable throught pair of item
        if not hasattr(mapping, 'iteritems'):
            res += "\t* Mapping must be iterable throught pairs of item\n\n"
        else:
            for model, columns in mapping.iteritems():
                # Check if model exist
                if model.startswith(self._relationnal_prefix):
                    model = model.split('::')[1]
                    columns = [columns]
                    self._session._logger.info(
                            "Checking relationnal model '%s' ..." % model,
                            extra=STATS[self._session.id])
                elif model.startswith('NO_CREATE'):
                    model = model.split('::')[1]
                    self._session._logger.info(
                            "Checking model (without creation) '%s' ..." % model,
                            extra=STATS[self._session.id])
                elif model.startswith('NO_UPDATE'):
                    model = model.split('::')[1]
                    self._session._logger.info(
                            "Checking model (without update) '%s' ..." % model,
                            extra=STATS[self._session.id])
                else:
                    self._session._logger.info(
                            "Checking model '%s' ..." % model,
                            extra=STATS[self._session.id])
                
                # Check if value is a well formed tuple
                for obj in columns:
                    if not hasattr(obj, 'iteritems'):
                        res += "\t* List of fields must be iterable \
throught pairs of item and objects (non relationnal) must be in a list.\n\n"
                        continue

                    for attr, tuple_val in deepcopy(obj).iteritems():
                        self._session._logger.debug(
                                "Checking field '%s'" % attr,
                                extra=STATS[self._session.id])
                        for patt in ACTION_PATTERN.values():
                            if attr.count(patt):
                                attr = attr.split('::')[1]
                        
                        try:
                            if callable(tuple_val):
                                tuple_val = tuple_val()[0]
                            (column, lambda_func, searchable) = tuple_val
                            if column is None and not callable(lambda_func):
                                res += "\t* You must indicate either a \
column number or a function or both in a field definition, \n\n"
                            required = False 
                            obj[attr] = (
                                    column,
                                    lambda_func,
                                    searchable,
                                    required)
                        except Exception as err:
                            print err
                            res += "\t* '%s' '%s' definition is not well \
formed, \n\n" % (model, attr)


        if res != "":
            raise Exception(title + res)
        else:
            return True
    
    #===========================================================================
    # Creation methods
    #===========================================================================
    def create(self, model, data, search=None):
        """Object's automatic and abstracted creation from model

        Logged public method
        
        :param model: Name of the OERP class model
        :type model: str
        :param data: Data dictionnary to transmit to OERP create/write method
        :type data: dict
        :param search: List of fields to be used for search
        :type search: list
        :returns: int 
        
        """
        if search is None:
            search = []
        if not data:
            return []
        (state, id_) = self._session._create(model, data, search)
        return id_

    def _fields_conversion(self, model, data):
        """Start fields conversion

        """
        search = []
        fields = []
        for field, value in data.iteritems():

            column = -1
            searchable = False
            required = False
            try:
                (column, callback, searchable) = value()[0]
            except:
                (column, callback, searchable, required) = value()[0]
            
            # Add this item to search criteria
            if searchable:
                search.append(field)
            fields.append(
                   models.fields.Field(
                       field,
                       column,
                       callback,
                       required=required)
                   )
        return fields, search

    def _models_conversion(self):
        """Start models conversion.

        """
        global SERVER
        models_tmp = []
        for model, datas in self._current_mapping.items():
            update = not model.count('NO_UPDATE')
            create = not model.count('NO_CREATE')
            try:
                model = model.split('::')[1]
            except:
                pass

            # Iterate through multiple model's instances
            for data in datas:
                fields, search = self._fields_conversion(model, data)
                
                # Create model and inject into models list
                model_tmp = models.Model(
                         model,
                         fields=fields,
                         create=create,
                         update=update,
                         search=search)
                models_tmp.append(model_tmp)
        return models_tmp

    def start(self):
        if self.check_mapping():
            models = self._models_conversion()
            self._session.bind(SERVER, models)
            return self._session.start()
        return False
    

class BaseField(object):
    
    def __init__(self, column, callback, search, attributes):
        if not column or isinstance(column, int):
            self.column = column
        elif isinstance(column, list):
            if column:
                for index in column:
                    if not isinstance(index, int):
                        raise Exception('Column\'s `column` argument must be a list of int or int')
                self.column = column
            else:
                raise Exception('Column\'s `column` argument must be a list of int or int')
        else:
            raise Exception('Column\'s `column` argument must be a list of int or int')
        if callback and not callable(callback):
            raise Exception('Column\'s `callback` argument must be callable')
        self.callback = callback
        if not isinstance(search, bool):
            raise Exception('Column\'s `search` argument must be a boolean')
        self.search = search
        if attributes and not isinstance(attributes, list):
            raise Exception('Column\'s `search` argument must be a list')
        self.attributes = attributes
    
    def __call__(self):
        return ((self.column, self.callback, self.search), self.attributes)


class Column(BaseField):
    """ Specify the column number and special treatments from which the current
    model's field will be allocated to the object's creation.
    Also declares metadatas for each model's field defined in mapping, like
    ``required``, ``readonly`` attributes.
    
    .. versionadded: 0.6

    Mapping example::
        
        >>> {
        ...     'model': {
        ...         'field': Column(column=0, callback=None, search=True),
        ...         } 
        ...     }

    :param column: The actual column number (mandatory)
    :type column: int
    :param callback: The actual callback function
    :type callback: function
    :param search: Search for same value before create object
    :type search: bool
    :param required: Is this field is required
    :type required: bool
    :param skip: Is this field is skippable
    :type skip: bool
    :param ignore: Is this field is ignorable (So object creation is skipped)
    :type ignore: bool
    :param replace: Is this field is replaceable (So it can be redifined)
    :type replace: bool
    :param noupdate: Is this field have not to be updated if existing in database
    :type noupdate: bool
    :param unique: Is this model's instance must be unique inside current model
    :type unique: bool

    """
    def __init__(self, column=None, callback=None, search=False,
            required=False, skip=False, ignore=False, replace=False,
            noupdate=False, unique=False):
        attributes = []
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Column, self).__init__(column, callback, search, attributes)
        
class Relation(BaseField):
    """ Specify a relation field.
    Also declares metadatas like ``required``, ``readonly`` attributes.
    
    .. versionadded: 0.6

    Mapping example::
        
        >>> {
        ...     'model': [
        ...         {
        ...             'field': Relation('REL_custom::model', search=True),
        ...             },
        ...         ],
        ...     'REL_custom::model': {
        ...         'field': Column(1),
        ...         }
        ...     }

    :param relation: The full name of the model which has to be related to field
    :type relation: str
    :param search: Search for same value before create object
    :type search: bool
    :param required: Is this field is required
    :type required: bool
    :param skip: Is this field is skippable
    :type skip: bool
    :param ignore: Is this field is ignorable (So object creation is skipped)
    :type ignore: bool
    :param replace: Is this field is replaceable (So it can be redifined)
    :type replace: bool
    :param noupdate: Is this field have not to be updated if existing in database
    :type noupdate: bool
    :param unique: Is this model's instance must be unique inside current model
    :type unique: bool

    """
    def __init__(self, relation, search=False, required=False, skip=False,
            noupdate=False, unique=False):
        callback = lambda *a: relation
        attributes = []
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Relation, self).__init__(None, callback, search, attributes)


class Custom(BaseField):
    """ Specify a custom value for current field.
    
    .. versionadded: 0.6

    Mapping example::
        
        >>> mapping = {
        ...     'model': {
        ...         'field': Custom('custom', search=True),
        ...         } 
        ...     }

    :param value: The value to apply.
    :type value: type
    :param search: Search for same value before create object
    :type search: bool

    """
    def __init__(self, value, search=False):
        attributes = []
        callback = lambda *a: value
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'search', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Custom, self).__init__(None, callback, search, attributes)
        
class Router(BaseField):
    """ Specify the column number and special treatments from which the current
    model's field will be allocated to the object's creation.
    Also declares metadatas for each model's field defined in mapping, like
    ``required``, ``readonly`` attributes.
    
    .. versionadded: 0.6

    Mapping example::
        >>> def _router(iself, model, field, value, line):
        ...     if value in 'some_value':
        ...         return {'field': {'f1':'val', 'f2':'val', 'f3':'val'}}
        >>> ...
        >>> {
        ...     'model': {
        ...         'field': Router(column=0, callback=_router),
        ...         } 
        ...     }

    :param column: The actual column number (mandatory)
    :type column: int
    :param callback: The actual callback function
    :type callback: function

    """
    def __init__(self, column=None, callback=None, **kwargs):
        attributes = []
        # Getting the calling frame from stack
        frame = stack()[0][0]
        # Arguments passed to the method
        frame_args = getargvalues(frame)
        # Reformatting to kwargs arguments
        kwargs = frame_args.locals
        # Cleaning kwargs from args
        for item in ('column', 'callback', 'frame', 'action'):
            if item in kwargs:
                del kwargs[item]
        for arg in kwargs:
            if kwargs[arg] and arg in ACTION_PATTERN:
                attributes.append(ACTION_PATTERN[arg])
        return super(Router, self).__init__(column, callback, False, attributes)
        
