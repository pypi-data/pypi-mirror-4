.. vim: set fileencoding=utf-8 :
.. @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
.. @date:   Thu Dec  6 12:28:25 CET 2012

=================================
 Verification Database Utilities
=================================

When you write an xbob.db database that should be used for verification (e.g. face verification), you should follow the structure provided by this package.
In order to assure compatibility with other verification databases, please:

1. derive your ``File`` class from ``xbob.db.verification.utils.File``
2. derive your ``Database`` class from ``xbob.db.verification.utils.Database``

and implement the desired abstract methods.
If your database uses the SQLite interface, you should directly derive your ``Database`` from ``xbob.db.verification.utils.SQLiteDatabase``.
If you also provide functions for dealing with ZT score normalization, please **also** derive your class from ``xbob.db.verification.utils.ZTDatabase``.
In any case, please call the corresponding base class constructor(s) in your constructor.


The ``File`` class
------------------

The ``File`` class provides the minimum common interface for a File object the can be queried from a ``Database``.
During construction, it requires the ID of the client to which this file belongs, and the relative path of the file.
Additionally, the ID of the file has to be specified, unless it is automatically initialized, e.g. by using the SQLite interface.

The ``File`` base class has some common functionality that might be used on files.
E.g. you can create an absolute path for a real file by calling ``File.make_path()``, specifying the desired directory and file name extension.


The ``Database`` classes
------------------------

The ``Database`` class and its derivatives ``SQLiteDatabase`` and ``ZTDatabase`` provide the minimum common interface for verification databases handled by Bob.
Please assure that all abstract methods are actually implemented, using at least the parameters as given in the base class.
If you miss one of the parameter names, you will get an exception during execution.

In the ``Database`` class, you have to implement:

1. ``model_ids(self, groups, protocol)``
2. ``objects(self, groups, protocol, purposes, model_ids)``

In ``ZTDatabase``, you additionally need to provide implementations for:

3. ``tmodel_ids(self, groups, protocol)``
4. ``tobjects(self, groups, protocol, model_ids)``
5. ``zobjects(self, groups, protocol)``

For a description of the parameters, please refer to the source code documentation.
In any case, your functions are allowed to take extra keyword arguments (but no non-keyword arguments).

The ``Database`` classes also provide some common functionality for testing valid arguments.
There are two functions: ``check_parameters_for_validity()`` and ``check_parameter_for_validity()`` (note the difference: parameters and parameter).
The first checks if the given list of parameters are contained in the list of valid parameters and returns a list of valid parameters.
The second check if the given single parameter is contained in the list of valid parameters and returns one valid parameter.

The ``SQLiteDatabase`` provides additional interfaces for dealing with the SQLite database.
On creation it opens a read-only connection to the given SQLite database and keeps it opened during the whole session.
To query the database, please use the ``SQLiteDatabase.query(...)`` function, which is just a wrapper class for the normal SQLite query and takes the same arguments.

