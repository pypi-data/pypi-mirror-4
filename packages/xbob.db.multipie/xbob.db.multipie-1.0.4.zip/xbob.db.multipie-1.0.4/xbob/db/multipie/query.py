#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""This module provides the Dataset interface allowing the user to query the
Multi-PIE database in the most obvious ways.
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
    # call base class constructors
    xbob.db.verification.utils.SQLiteDatabase.__init__(self, SQLITE_FILE, File)
    xbob.db.verification.utils.ZTDatabase.__init__(self)

  def groups(self):
    """Returns the names of all registered groups"""

    return ProtocolPurpose.group_choices # Same as Client.group_choices for this database

  def genders(self):
    """Returns the list of genders"""

    return Client.gender_choices

  def subworlds(self):
    """Returns the list of subworlds"""

    return list(self.query(Subworld))

  def has_subworld(self, name):
    """Tells if a certain subworld is available"""

    return self.query(Subworld).filter(Subworld.name==name).count() != 0

  def subworld_names(self):
    """Returns all registered subworld names"""

    l = self.subworlds()
    retval = [str(k.name) for k in l]
    return retval

  def expressions(self):
    """Returns the list of expressions"""

    return list(self.query(Expression))

  def has_expression(self, name):
    """Tells if a certain expression is available"""

    return self.query(Expression).filter(Expression.name==name).count() != 0

  def expression_names(self):
    """Returns all registered expression names"""

    l = self.expressions()
    retval = [str(k.name) for k in l]
    return retval

  def cameras(self):
    """Returns the list of cameras"""

    return list(self.query(Camera))

  def has_camera(self, name):
    """Tells if a certain camera is available"""

    return self.query(Camera).filter(Camera.name==name).count() != 0

  def camera_names(self):
    """Returns all registered camera names"""

    return [str(c.name) for c in self.cameras()]

  def clients(self, protocol=None, groups=None, subworld=None, genders=None, birthyears=None):
    """Returns a set of Clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the clients belong ('dev', 'eval', 'world')

    subworld
      Specify a split of the world data ('sub41', 'sub81', 'sub121', 'sub161')
      In order to be considered, "world" should be in groups.

    genders
      The genders to which the clients belong ('female', 'male')

    birthyears
      The birth year of the clients (in the range [1900,2050])

    Returns: A list containing all the Clients which have the given properties.
    """

    VALID_BIRTHYEARS = range(1900, 2050)
    VALID_BIRTHYEARS.append(57) # bug in subject_list.txt (57 instead of 1957)
    protocol = self.check_parameters_for_validity(protocol, 'protocol', self.protocol_names())
    groups = self.check_parameters_for_validity(groups, 'group', self.groups())
    if subworld:
      subworld = self.check_parameters_for_validity(subworld, 'subworld', self.subworld_names())
    genders = self.check_parameters_for_validity(genders, 'gender', self.genders())
    birthyears = self.check_parameters_for_validity(birthyears, 'birthyear', VALID_BIRTHYEARS)

    # List of the clients
    retval = []
    # World data
    if "world" in groups:
      q = self.query(Client)
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
      q = q.filter(Client.sgroup == 'world').\
            filter(Client.gender.in_(genders)).\
            filter(Client.birthyear.in_(birthyears)).\
            order_by(Client.id)
      retval += list(q)
    # dev / eval data
    if 'dev' in groups or 'eval' in groups:
      q = self.query(Client).\
            filter(and_(Client.sgroup != 'world', Client.sgroup.in_(groups))).\
            filter(Client.gender.in_(genders)).\
            filter(Client.birthyear.in_(birthyears)).\
            order_by(Client.id)
      retval += list(q)
    return retval

  def has_client_id(self, id):
    """Returns True if we have a client with a certain integer identifier"""

    return self.query(Client).filter(Client.id==id).count() != 0

  def client(self, id):
    """Returns the Client object in the database given a certain id. Raises
    an error if that does not exist."""

    return self.query(Client).filter(Client.id==id).one()

  def tclients(self, protocol=None, groups=None):
    """Returns a set of T-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the clients belong ('dev', 'eval').

    Returns: A list containing all the client ids belonging to the given group.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))
    tgroups = []
    if 'dev' in groups: tgroups.append('eval')
    if 'eval' in groups: tgroups.append('dev')
    return self.clients(protocol, tgroups)

  def zclients(self, protocol=None, groups=None):
    """Returns a set of Z-Norm clients for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the clients belong ('dev', 'eval').

    Returns: A list containing all the client ids belonging to the given group.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))
    zgroups = []
    if 'dev' in groups: zgroups.append('eval')
    if 'eval' in groups: zgroups.append('dev')
    return self.clients(protocol, zgroups)

  def models(self, protocol=None, groups=None):
    """Returns a set of models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing all the models belonging to the given group.
    """

    return self.clients(protocol, groups)

  def model_ids(self, protocol=None, groups=None):
    """Returns a set of model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the subjects attached to the models belong ('dev', 'eval', 'world')

    Returns: A list containing the ids all the models belonging to the given group.
    """

    return [client.id for client in self.clients(protocol, groups)]

  def tmodels(self, protocol=None, groups=None):
    """Returns a set of T-Norm models for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the models belong ('dev', 'eval').

    Returns: A list containing all the T-Norm models belonging to the given group.
    """

    return self.tclients(protocol, groups)

  def tmodel_ids(self, protocol=None, groups=None):
    """Returns a set of T-Norm model ids for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    groups
      The groups to which the models belong ('dev', 'eval').

    Returns: A list containing all ids of the T-Norm models belonging to the given group.
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
      classes=None, subworld=None, expressions=None, cameras=None, world_sampling=1,
      world_noflash=False, world_first=False, world_second=False, world_third=False,
      world_fourth=False, world_nshots=None, world_shots=None):
    """Returns a set of Files for the specific query by the user.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    purposes
      The purposes required to be retrieved ('enrol', 'probe', 'train') or a tuple
      with several of them. If 'None' is given (this is the default), it is
      considered the same as a tuple with all possible values. This field is
      ignored for the data from the "world" group.

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      One of the groups ('dev', 'eval', 'world') or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as a
      tuple with all possible values.

    classes
      The classes (types of accesses) to be retrieved ('client', 'impostor')
      or a tuple with several of them. If 'None' is given (this is the
      default), it is considered the same as a tuple with all possible values.

    subworld
      Specify a split of the world data ('sub41', 'sub81', 'sub121', 'sub161')
      In order to be considered, "world" should be in groups.

    expressions
      The (face) expressions to be retrieved (use expression_names() to get the
      list of expressions) or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as
      a tuple with all possible values. Notice that some protocols only contain
      images with 'neutral' expression.

    cameras
      The cameras to be retrieved (use camera_names() to get the list of cameras)
      r a tuple with several of them. If 'None' is given (this is the default),
      it is considered the same as a tuple with all possible values. The cameras
      keyword has no impact for some protocols (frontal images ones).

    world_sampling
      Samples the files from the world data set. Keeps only files such as::

        File.client_id + File.shot_id % world_sampling == 0

      This argument should be an integer between 1 (keep everything) and 19.
      It is not used if world_noflash is also set.

    world_nshots
      Only considers the n first shots from the world data set.

    world_shots
      Only considers the shots with the given ids.

    world_noflash
      Keeps the files from the world dataset recorded without flash (shot 0)

    world_first
      Only uses data from the first recorded session of each user of the world
      dataset.

    world_second
      Only uses data from the second recorded session of each user of the world
      dataset.

    world_third
      Only uses data from the third recorded session of each user of the world
      dataset.

    world_fourth
      Only uses data from the fourth recorded session of each user of the world
      dataset.

    Returns: A set of Files with the given properties.
    """

    protocol = self.check_parameters_for_validity(protocol, 'protocol', self.protocol_names())
    purposes = self.check_parameters_for_validity(purposes, 'purpose', self.purposes())
    groups = self.check_parameters_for_validity(groups, 'group', self.groups())
    classes = self.check_parameters_for_validity(classes, 'class', ('client', 'impostor'))
    if subworld:
      subworld = self.check_parameters_for_validity(subworld, 'subworld', self.subworld_names())
    if expressions: expressions = self.check_parameters_for_validity(expressions, 'expression', self.expression_names())
    if cameras: cameras = self.check_parameters_for_validity(cameras, 'camera', self.camera_names())

    import collections
    if(model_ids is None):
      model_ids = ()
    elif(not isinstance(model_ids,collections.Iterable)):
      model_ids = (model_ids,)

    # Now query the database
    retval = []
    if 'world' in groups:
      q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                  filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup == 'world'))
      if subworld:
        q = q.join((Subworld, Client.subworld)).filter(Subworld.name.in_(subworld))
      if expressions:
        q = q.join(Expression).filter(Expression.name.in_(expressions))
      if cameras:
        q = q.join(FileMultiview).join(Camera).filter(Camera.name.in_(cameras))
      if(world_nshots):
        max1 = 19
        max2 = 19
        max3 = 19
        max4 = 19
        if world_nshots < 19:
          max1 = world_nshots
          max2 = 0
          max3 = 0
          max4 = 0
        elif world_nshots < 38:
          max2 = world_nshots - 19
          max3 = 0
          max4 = 0
        elif world_nshots < 57:
          max3 = world_nshots - 38
          max4 = 0
        else:
          max4 = world_nshots - 57
        q = q.filter(or_( and_( File.session_id == Client.first_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max1),
                                                                             and_(File.recording_id == 2, FileMultiview.shot_id < max2))),
                          and_( File.session_id == Client.second_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max2),
                                                                              and_(File.recording_id == 2, FileMultiview.shot_id < max3))),
                          and_( File.session_id == Client.third_session, or_(and_(File.recording_id == 1, FileMultiview.shot_id < max3),
                                                                             and_(File.recording_id == 2, FileMultiview.shot_id < max4))),
                          and_( File.session_id == Client.fourth_session, FileMultiview.shot_id < max4)))
      if(world_shots):
        q = q.filter(FileMultiview.shot_id.in_(world_shots))
      if( world_sampling != 1 and world_noflash == False):
        q = q.filter(((File.client_id + FileMultiview.shot_id) % world_sampling) == 0)
      if( world_noflash == True):
        q = q.filter(FileMultiview.shot_id == 0)
      if( world_first == True):
        q = q.filter(and_(File.session_id == Client.first_session, or_(Client.first_session != 4,
                  and_(Client.first_session == 4, File.recording_id == 1))))
      if( world_second == True):
        q = q.filter(or_( and_(Client.second_session != 4, File.session_id == Client.second_session),
                          or_( and_(Client.first_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.second_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      if( world_third == True):
        q = q.filter(or_( and_(Client.third_session != 4, File.session_id == Client.third_session),
                          or_( and_(Client.second_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.third_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      if( world_fourth == True):
        q = q.filter(or_( and_(Client.fourth_session != 4, File.session_id == Client.fourth_session),
                          or_( and_(Client.third_session == 4, and_(File.session_id == 4, File.recording_id == 2)),
                               and_(Client.fourth_session == 4, and_(File.session_id == 4, File.recording_id == 1)))))
      if model_ids:
        q = q.filter(Client.id.in_(model_ids))
      q = q.order_by(File.client_id, File.session_id, File.recording_id, File.id)
      retval += list(q)

    if ('dev' in groups or 'eval' in groups):
      if('enrol' in purposes):
        q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
              filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'enrol'))
        if expressions:
          q = q.join(Expression).filter(Expression.name.in_(expressions))
        if cameras:
          q = q.join(FileMultiview).join(Camera).filter(Camera.name.in_(cameras))
        if model_ids:
          q = q.filter(Client.id.in_(model_ids))
        q = q.order_by(File.client_id, File.session_id, File.recording_id, File.id)
        retval += list(q)

      if('probe' in purposes):
        if('client' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if expressions:
            q = q.join(Expression).filter(Expression.name.in_(expressions))
          if cameras:
            q = q.join(FileMultiview).join(Camera).filter(Camera.name.in_(cameras))
          if model_ids:
            q = q.filter(Client.id.in_(model_ids))
          q = q.order_by(File.client_id, File.session_id, File.recording_id, File.id)
          retval += list(q)

        if('impostor' in classes):
          q = self.query(File).join(Client).join((ProtocolPurpose, File.protocol_purposes)).join(Protocol).\
                filter(and_(Protocol.name.in_(protocol), ProtocolPurpose.sgroup.in_(groups), ProtocolPurpose.purpose == 'probe'))
          if expressions:
            q = q.join(Expression).filter(Expression.name.in_(expressions))
          if cameras:
            q = q.join(FileMultiview).join(Camera).filter(Camera.name.in_(cameras))
          if len(model_ids) == 1:
            q = q.filter(not_(Client.id.in_(model_ids)))
          q = q.order_by(File.client_id, File.session_id, File.recording_id, File.id)
          retval += list(q)

    return list(set(retval)) # To remove duplicates

  def tobjects(self, protocol=None, model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames for enrolling T-norm models for score
       normalization.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    model_ids
      Only retrieves the files for the provided list of model ids (claimed
      client id).  If 'None' is given (this is the default), no filter over
      the model_ids is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved (use expression_names() to get the
      list of expressions) or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as
      a tuple with all possible values. Notice that some protocols only contain
      images with 'neutral' expression.

    Returns: A list of Files with the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    tgroups = []
    if 'dev' in groups:
      tgroups.append('eval')
    if 'eval' in groups:
      tgroups.append('dev')
    return self.objects(protocol, 'enrol', model_ids, tgroups, 'client', None, expressions)

  def zobjects(self, protocol=None, model_ids=None, groups=None, expressions=None):
    """Returns a set of filenames of impostors for Z-norm score normalization.

    Keyword Parameters:

    protocol
      One of the Multi-PIE protocols (use protocol_names() to get the list of
      available ones)

    model_ids
      Only retrieves the files for the provided list of model ids (client id).
      If 'None' is given (this is the default), no filter over the model_ids
      is performed.

    groups
      The groups to which the clients belong ('dev', 'eval').

    expressions
      The (face) expressions to be retrieved (use expression_names() to get the
      list of expressions) or a tuple with several of them.
      If 'None' is given (this is the default), it is considered the same as
      a tuple with all possible values. Notice that some protocols only contain
      images with 'neutral' expression.

    Returns: A list of Files with the given properties.
    """

    groups = self.check_parameters_for_validity(groups, "group", ('dev', 'eval'))

    zgroups = []
    if 'dev' in groups:
      zgroups.append('eval')
    if 'eval' in groups:
      zgroups.append('dev')
    return self.objects(protocol, 'probe', model_ids, zgroups, 'client', None, expressions)

  def protocol_names(self):
    """Returns all registered protocol names"""

    return [str(p.name) for p in self.protocols()]

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

