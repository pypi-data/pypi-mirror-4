#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Manuel Guenther <Manuel.Guenther@idiap.ch>
# @date:   Thu Dec  6 12:28:25 CET 2012
#
# Copyright (C) 2011-2012 Idiap Research Institute, Martigny, Switzerland
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# helper functions
def check_parameters_for_validity(parameters, parameter_description, valid_parameters, default_parameters = None):
  """Checks the given parameters for validity, i.e., if they are contained in the set of valid parameters.
  It also assures that the parameters form a tuple or a list.
  If parameters is 'None' or empty, the default_parameters will be returned (if default_parameters is omitted, all valid_parameters are returned).

  This function will return a tuple or list of parameters, or raise a ValueError.

  Keyword parameters:

  parameters
    The parameters to be checked.
    Might be a string, a list/tuple of strings, or None.

  parameter_description
    A short description of the parameter.
    This will be used to raise an exception in case the parameter is not valid.

  valid_parameters
    A list/tuple of valid values for the parameters.

  default_parameters
    The list/tuple of default parameters that will be returned in case parameters is None or empty.
    If omitted, all valid_parameters are used.
  """
  if not parameters:
    # parameters are not specified, i.e., 'None' or empty lists
    parameters = default_parameters if default_parameters else valid_parameters

  if not isinstance(parameters, (list, tuple)):
    # parameter is just a single element, not a tuple or list -> transform it into a tuple
    parameters = (parameters,)

  # perform the checks
  for parameter in parameters:
    if parameter not in valid_parameters:
      raise ValueError, "Invalid %s '%s'. Valid values are %s, or lists/tuples of those" % (parameter_description, parameter, valid_parameters)

  # check passed, now return the list/tuple of parameters
  return parameters


def check_parameter_for_validity(parameter, parameter_description, valid_parameters, default_parameter = None):
  """Checks the given parameter for validity, i.e., if it is contained in the set of valid parameters.
  If the parameter is 'None' or empty, the default_parameter will be returned, in case it is specified, otherwise a ValueError will be raised.

  This function will return the parameter after the check tuple or list of parameters, or raise a ValueError.

  Keyword parameters:

  parameter
    The single parameter to be checked.
    Might be a string or None.

  parameter_description
    A short description of the parameter.
    This will be used to raise an exception in case the parameter is not valid.

  valid_parameters
    A list/tuple of valid values for the parameters.

  default_parameters
    The default parameter that will be returned in case parameter is None or empty.
    If omitted and parameter is empty, a ValueError is raised.
  """
  if not parameter:
    # parameter not specified ...
    if default_parameter:
      # ... -> use default parameter
      parameter = default_parameter
    else:
      # ... -> raise an exception
      raise ValueError, "The %s has to be one of %s, it might not be 'None'." % (parameter_description, valid_parameters)

  if isinstance(parameter, (list, tuple)):
    # the parameter is in a list/tuple ...
    if len(parameter) > 1:
      raise ValueError, "The %s has to be one of %s, it might not be more than one (%s was given)." % (parameter_description, valid_parameters, parameter)
    # ... -> we take the first one
    parameter = parameter[0]

  # perform the check
  if parameter not in valid_parameters:
    raise ValueError, "The given %s '%s' is not allowed. Please choose one of %s." % (parameter_description, parameter, valid_parameters)

  # tests passed -> return the parameter
  return parameter

