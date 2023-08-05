###############################################################################
#
# Copyright (c) 2009 Projekt01 GmbH.
# All Rights Reserved.
#
###############################################################################
"""
$Id:$
"""

import zope.interface
import zope.schema
import z3c.schema.email


class IDataGenerator(zope.interface.Interface):
    """Base functionality for data generators."""

    random = zope.interface.Attribute(
        '''An instance of the standard Python random number generator. This
        attribute is public, so that tests can implement predictable versions
        -- for example by setting the same seed all the time.''')

    def get(self):
        """Select a value from the values list and return it."""

    def getMany(self, number):
        """Select a set of values from the values list and return them."""


class IFileBasedGenerator(IDataGenerator):
    """Data generator using a single file extract data.

    Specific implementations include a simple line-based and a CSV one.
    """

    path = zope.interface.Attribute(
        'The path to the file providing the data.')


class IDateDataGenerator(IDataGenerator):
    """A date data generator.

    This generator creates dates/times between the start and end dates/times.
    """

    start = zope.schema.Datetime(
        title=u'Start Date/Time',
        description=u'This field descibres the earliest date/time generated.',
        required=True)

    end = zope.schema.Datetime(
        title=u'End Date/Time',
        description=u'This field descibres the latest date/time generated.',
        required=True)

    def get(self, start=None, end=None):
        """Create a new date between the start and end date.

        The start and end date/time can be overridden here, since you
        sometimes want to generate sequences of dates.
        """


class IMemberData(zope.interface.Interface):
    """Member data."""

    __name__ = zope.schema.TextLine(
        title=u'Principal ID (pid)',
        description=u'The name of the user.',
        readonly=False)

    nickName = zope.schema.TextLine(
        title=u'Nick Name',
        description=u'The nick name of the user.',
        readonly=False)

    login = zope.schema.TextLine(
        title=u'Login',
        description=u'The login name of the user.')

    password = zope.schema.Password(
        title=u'Password',
        description=u'The password of the user.')

    email = z3c.schema.email.field.RFC822MailAddress(
        title=u'Email',
        description=u'The email address of the user.',
        required=True)

    group = zope.schema.TextLine(
        title=u'Group',
        description=u'The group member, company or recruiter.')


class IEmployerData(IMemberData):
    """Employer data."""


class IRecruiterData(IMemberData):
    """Recruiter data."""
