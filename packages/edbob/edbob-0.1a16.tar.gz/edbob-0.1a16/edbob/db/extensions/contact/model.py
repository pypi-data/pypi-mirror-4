#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  edbob -- Pythonic Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of edbob.
#
#  edbob is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  edbob is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with edbob.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``edbob.db.extensions.contact.model`` -- Schema Definition
"""

from sqlalchemy import Column, String, Integer
from sqlalchemy import and_
from sqlalchemy.orm import relationship
from sqlalchemy.ext.orderinglist import ordering_list

from edbob.db.model import Base, uuid_column


__all__ = ['PhoneNumber', 'Person', 'PersonPhoneNumber', 'EmailAddress',
           'PersonEmailAddress']


def get_person_display_name(context):
    """
    Provides a default value for :attr:`Person.display_name`, constructed from
    :attr:`Person.first_name` and :attr:`Person.last_name`.
    """

    first_name = context.current_parameters['first_name']
    last_name = context.current_parameters['last_name']
    if first_name and last_name:
        return first_name + ' ' + last_name
    if first_name:
        return first_name
    if last_name:
        return last_name
    return None


class PhoneNumber(Base):
    """
    Represents a phone (or fax) number associated with a contactable entity.
    """

    __tablename__ = 'phone_numbers'

    uuid = uuid_column()
    parent_type = Column(String(20), nullable=False)
    parent_uuid = Column(String(32), nullable=False)
    preference = Column(Integer, nullable=False)
    type = Column(String(15))
    number = Column(String(20), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.number)

    def __unicode__(self):
        return unicode(self.number)


class PersonPhoneNumber(PhoneNumber):
    """
    Represents a phone (or fax) number associated with a :class:`Person`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


class EmailAddress(Base):
    """
    Represents an email address associated with a contactable entity.
    """

    __tablename__ = 'email_addresses'

    uuid = uuid_column()
    parent_type = Column(String(20), nullable=False)
    parent_uuid = Column(String(32), nullable=False)
    preference = Column(Integer, nullable=False)
    type = Column(String(15))
    address = Column(String(255), nullable=False)

    __mapper_args__ = {'polymorphic_on': parent_type}

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.address)

    def __unicode__(self):
        return unicode(self.address)


class PersonEmailAddress(EmailAddress):
    """
    Represents an email address associated with a :class:`Person`.
    """

    __mapper_args__ = {'polymorphic_identity': 'Person'}


class Person(Base):
    """
    Represents a real, living and breathing person.  (Or, at least was
    previously living and breathing, in the case of the deceased.)
    """

    __tablename__ = 'people'

    uuid = uuid_column()
    first_name = Column(String(50))
    last_name = Column(String(50))
    display_name = Column(String(100), default=get_person_display_name)

    def __repr__(self):
        return "<Person: %s>" % self.display_name

    def __unicode__(self):
        return unicode(self.display_name or '')

    def add_email_address(self, address, type='Home'):
        email = PersonEmailAddress(address=address, type=type)
        self.emails.append(email)

    def add_phone_number(self, number, type='Home'):
        phone = PersonPhoneNumber(number=number, type=type)
        self.phones.append(phone)

Person.emails = relationship(
    PersonEmailAddress,
    backref='person',
    primaryjoin=PersonEmailAddress.parent_uuid == Person.uuid,
    foreign_keys=[PersonEmailAddress.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonEmailAddress.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.email = relationship(
    PersonEmailAddress,
    primaryjoin=and_(
        PersonEmailAddress.parent_uuid == Person.uuid,
        PersonEmailAddress.preference == 1,
        ),
    foreign_keys=[PersonEmailAddress.parent_uuid],
    uselist=False,
    viewonly=True)

Person.phones = relationship(
    PersonPhoneNumber,
    backref='person',
    primaryjoin=PersonPhoneNumber.parent_uuid == Person.uuid,
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    collection_class=ordering_list('preference', count_from=1),
    order_by=PersonPhoneNumber.preference,
    cascade='save-update, merge, delete, delete-orphan')

Person.phone = relationship(
    PersonPhoneNumber,
    primaryjoin=and_(
        PersonPhoneNumber.parent_uuid == Person.uuid,
        PersonPhoneNumber.preference == 1,
        ),
    foreign_keys=[PersonPhoneNumber.parent_uuid],
    uselist=False,
    viewonly=True)
