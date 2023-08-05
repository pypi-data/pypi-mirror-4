#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""This module provides the Dataset interface allowing the user to query the
SCFace database in the most obvious ways.
"""

import os
from bob.db import utils
from .models import *
from .driver import Interface

import xbob.db.verification.utils

SQLITE_FILE = Interface().files()[0]

class Database(xbob.db.verification.utils.SQLiteDatabase, xbob.db.verification.utils.ZTDatabase):
  """The dataset class opens and maintains a connection opened to the Database.

  It provides many different ways to probe for the characteristics of the data
  and for the data itself inside the database.
  """

  def __init__(self):
    # call base class constructors to open a session to the database
    xbob.db.verification.utils.SQLiteDatabase.__init__(self, SQLITE_FILE, File)
    xbob.db.verification.utils.ZTDatabase.__init__(self)

  def groups(self):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices # Same as Client.group_choices for this database

  def genders(self):
    """Returns the list of genders: 'm' for male and 'f' for female"""

    return Client.gender_choices

  def subworld_names(self):
    """Returns all registered subworld names"""

    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    return self.query(Subworld).filter(Subworld.name==name).count() != 0

  def clients(self, protocol=None, groups=None, subworld=None, gender=None, birthyear=None):
    """Returns a set of Clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    subworld
      Specify a split of the world data ("onethird", "twothirds", "")
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    gender
      The genders to which the clients belong ('f', 'm')

    birthyear
      The birth year of the clients (in the range [1900,2050])

    Returns: A list containing all the clients which have the given
    properties.
    """

    protocol = self.check_parameters_for_validity(protocol, 'protocol', self.protocol_names())
    groups = self.check_parameters_for_validity(groups, 'group', self.groups())
    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])
    gender = self.check_parameters_for_validity(gender, "gender", self.genders(), [])
    birthyear = self.check_parameters_for_validity(birthyear, 'birthyear', range(1900,2050), [])

    retval = []
    # List of the clients
    if "world" in groups:
      q = self.query(Client).filter(Client.sgroup == 'world')
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if birthyear:
        q = q.filter(Client.birthyear.in_(birthyear))
      q = q.order_by(Client.id)
      retval += list(q)
    if 'dev' in groups or 'eval' in groups:
      q = self.query(Client).filter(and_(Client.sgroup != 'world', Client.sgroup.in_(groups)))
      if gender:
        q = q.filter(Client.gender.in_(gender))
      if birthyear:
        q = q.filter(Client.birthyear.in_(birthyear))
      q = q.order_by(Client.id)
      retval += list(q)
    return retval

  def tclients(self, protocol=None, groups=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing all the clients belonging to the given group.
    """

    # T-Norm clients are the ones from the onethird world subset
    return self.clients(protocol, 'world', 'onethird')

  def zclients(self, protocol=None, groups=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    # Z-Norm clients are the ones from the onethird world subset
    return self.clients(protocol, 'world', 'onethird')

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a set of models ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing the ids of all models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups)]

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    self.assert_validity()
    return self.query(Client).filter(Client.id==id).count() != 0

  def client(self, id):
    """Returns the Client object in the database given a certain id. Raises
    an error if that does not exist."""

    self.assert_validity()
    return self.query(Client).filter(Client.id==id).one()

  def tmodels(self, protocol=None, groups=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing all the T-Norm models.
    """

    return self.tclients(protocol, groups)

  def tmodel_ids(self, protocol=None, groups=None):
    """Returns a set of T-Norm model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      The protocol to consider ('combined', 'close', 'medium', 'far')

    groups
      Ignored.

    Returns: A list containing the ids of all T-Norm models.
    """
    return [client.id for client in self.tclients(protocol, groups)]

  def get_client_id_from_model_id(self, model_id):
    """Returns the client_id attached to the given model_id

    Keyword Parameters:

    model_id
      The model_id to consider

    Returns: The client_id attached to the given model_id
    """
    return model_id

  def objects(self, protocol=None, purposes=None, model_ids=None, groups=None,
      classes=None, subworld=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    purposes
      The purposes required to be retrieved ('enrol', 'probe', 'world') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id). The model ids are string.  If 'None' is given (this is
      the default), no filter over the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    subworld
      Specify a split of the world data ("onethird", "twothirds", "")
      In order to be considered, "world" should be in groups and only one
      split should be specified.

    Returns: A list of Files with the given properties
    """

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, "purpose", self.purposes())
    groups = self.check_parameters_for_validity(groups, "group", self.groups())
    classes = self.check_parameters_for_validity(classes, "class", ('client', 'impostor'))
    subworld = self.check_parameters_for_validity(subworld, "subworld", self.subworld_names(), [])

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol)
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
      q = q.filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world'))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.camera, File.distance, File.id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enrol' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'enrol'))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.camera, File.distance, File.id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.camera, File.distance, File.id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if len(model_ids) == 1:
            q = q.filter(not_(File.client_id.in_(model_ids)))
          q = q.order_by(File.client_id, File.camera, File.distance, File.id)
          retval += list(q)

    return list(set(retval)) # To remove duplicates


  def tobjects(self, protocol=None, model_ids=None, groups=None):
    """Returns a set of Files for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    Returns: A set of Files with the given properties
    """

    # ZT-Norm cohort is 'onethird'
    subworld = ('onethird',)
    # WARNING: Restrict to frontal camera (enrol T-Norm models)
    validcam = ('frontal',)

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                     join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld)).\
                     filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world', File.camera.in_(validcam)))
    if model_ids:
      q = q.filter(Client.id.in_(model_ids))
    q = q.order_by(File.client_id, File.camera, File.distance, File.id)
    retval += list(q)

    return retval

  def zobjects(self, protocol=None, model_ids=None, groups=None):
    """Returns a set of Files to perform Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the SCFace protocols ('combined', 'close', 'medium', 'far')

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      Ignored.

    Returns: A set of Files
    """

    # ZT-Norm cohort is 'onethird'
    subworld = ('onethird',)
    # WARNING: Restrict to non-frontal camera (enrol T-Norm models)
    validcam = ('cam1','cam2','cam3','cam4','cam5')

    protocol = self.check_parameters_for_validity(protocol, "protocol", self.protocol_names())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    retval = []
    q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                     join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld)).\
                     filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world', File.camera.in_(validcam)))
    if model_ids:
      q = q.filter(Client.id.in_(model_ids))
    q = q.order_by(File.client_id, File.camera, File.distance, File.id)
    retval += list(q)

    return retval

  def protocol_names(self):
    """Returns all registered protocol names"""

    l = self.protocols()
    retval = [str(k.name) for k in l]
    return retval

  def protocols(self):
    """Returns all registered protocols"""

    return list(self.query(Protocol))

  def has_protocol(self, name):
    """Tells if a certain protocol is available"""

    return self.query(Protocol).filter(Protocol.name==name).count() != 0

  def protocol(self, name):
    """Returns the protocol object in the database given a certain name. Raises
    an error if that does not exist."""

    return self.query(Protocol).filter(Protocol.name==name).one()

  def protocol_purposes(self):
    """Returns all registered protocol purposes"""

    return list(self.query(ProtocolPurpose))

  def purposes(self):
    """Returns the list of allowed purposes"""

    return ProtocolPurpose.purpose_choices

