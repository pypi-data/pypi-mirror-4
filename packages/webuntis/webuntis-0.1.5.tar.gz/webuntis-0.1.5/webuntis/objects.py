'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''

from __future__ import unicode_literals
from webuntis.utils import datetime_utils, lazyproperty, \
    timetable_utils


class Result(object):
    '''Base class used to represent most API objects.

    :param parent: (optional) A result object this result should be the child
                    of. If given, the session will be inherited.

    :param session: Mandatory if ``parent`` is not supplied. Overrides the
                    parent's inherited session.

    :param kwargs: Keyword arguments in form of a dictionary from the
                   higer-level wrapper-methods of
                   :py:class:`webuntis.session.Session`, for example
                   ``s.klassen``.

    :param data: Usually JSON data that should be represented.

                 In the case of :py:class:`ListResult`, however, it might also
                 be a list of JSON mixed with :py:class:`ListItem` objects.

                 If this is given, ``kwargs`` must not be supplied.
    '''

    _parent = None
    _session = None
    _kwargs = None
    _data = None

    #: The JSON-RPC method used to fetch the data
    _jsonrpc_method = None

    def __init__(self, parent=None, session=None, kwargs=None, data=None):
        if bool(kwargs is None) == bool(data is None):
            raise TypeError('Exactly one argument must be supplied: '
                            'kwargs, data')

        if not isinstance(parent, Result) and parent is not None:
            raise TypeError('If provided, parent must be an instance of '
                            'webuntis.objects.Result.')

        if bool(parent is None) == bool(session is None):
            raise TypeError('Either parent or session has to be provided.')

        self._session = session or parent._session
        self._parent = parent
        self._kwargs = kwargs
        self._data = data

    def _jsonrpc_parameters(self, **kwargs):
        '''This method returns all methods that should be passed to the
        JSON-RPC request'''
        # we return an empty dictionary here so subclasses don't
        # really need to overwrite this if they actually have no parameters
        return {}

    def get_data(self):
        '''A simple wrapper for the jsonrpc_parameters builder.
        Can be overwritten by subclasses, which may require more complex
        options'''
        if not self._jsonrpc_method:
            raise NotImplementedError

        if self._data is not None:
            raise Exception('We already have data!')

        self._data = self._session._request(
            self._jsonrpc_method,
            self._jsonrpc_parameters(**self._kwargs)
        )

    @lazyproperty
    def id(self):
        '''the ID of this element. When dealing with arrays as result, it is
        very common for an item to have its own ID.'''
        return self._data['id'] if 'id' in self._data else None

    def __int__(self):
        '''This is useful if the users pass a ListItem when a numerical ID
        is expected, so we just can put the thing through int(), regardless of
        what type it is.'''
        return self.id


class ListItem(Result):
    '''ListItems represent an item in a
    :py:class:`Result`. They don\'t contain methods to
    retrieve data.'''


class ListResult(Result):
    '''A list-like version of :py:class:`Result` that takes a list and returns
    a list of objects, containing a list value each.

    :py:class:`ListResult` instances now have support for ``__contains__``,
    which means you can do::

        we_have_it = {'name': '6A'} in s.klassen()

    instead of::

        we_have_it = bool(s.klassen().filter(name='6A'))
    '''

    # When the Result returns an array, this is very useful. Every item of that
    # array will be fed to an instance of self._itemclass, with the session and
    # the array item as initialization arguments.

    #: the class which should be used to instantiate an array item.
    _itemclass = ListItem

    #: Contains the object representation of each item found in _data. Is a
    #: dictionary instead of a list to allow random r/w access without
    #: IndexErrors.
    _itemcache = None

    def __init__(self, *args, **kwargs):
        Result.__init__(self, *args, **kwargs)
        self._itemcache = {}

    def filter(self, **criterions):
        '''
        Return a list of all objects, filtered by attributes::

            foo = s.klassen().filter(id=1)  # is the same as
            foo = [kl for kl in s.klassen() if kl.id == 1]

            # We can also use sets to match multiple values.
            bar = s.klassen().filter(name={'1A', '2A', '3A', '4A'})
            # is the same as
            bar = [kl for kl in s.klassen()
                   if kl.id in {'1A', '2A', '3A', '4A'}]

            # Since ``filter`` returns a ListResult itself too, we can chain
            # multiple calls together:
            bar = s.klassen().filter(id=4, name='7A')  # is the same as
            bar = s.klassen().filter(id=4).filter(name='7A')

        .. note::
            This is only available because it looks nicer than list
            comprehensions or generator expressions. Depending on your usecase
            alternatives to this method may be faster.
        ::
        '''
        criterions = list(criterions.items())

        def meets_criterions(item):
            '''Returns true if the item meets the criterions'''
            for key, value in criterions:
                # if the attribute value isn't one we're looking for
                attribute = getattr(item, key)
                if attribute == value:
                    continue
                elif isinstance(value, set) and attribute in value:
                    continue
                else:
                    return False

            return True

        return type(self)(
            parent=self,
            data=[item for item in self if meets_criterions(item)]
        )

    def __contains__(self, criterion):
        return bool(self.filter(**criterion))

    def __getitem__(self, i):
        '''Makes the object iterable and behave like a list'''
        data = self._data[i]  # fails if there is no such item

        try:
            value = self._itemcache[i]
        except KeyError:
            # if we don't have an object yet
            if type(data) is not self._itemclass:
                self._itemcache[i] = value = self._itemclass(
                    parent=self,
                    data=data
                )
            else:
                self._itemcache[i] = value = data


        return value

    def __len__(self):
        '''Return the length of the items'''
        return len(self._data)


class DepartmentObject(ListItem):
    '''Represents a department'''

    @lazyproperty
    def name(self):
        '''short name such as *R1A*'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name, such as *Raum Erste A*. Not predictable.'''
        return self._data['longName']


class DepartmentList(ListResult):
    '''A list of all departments::

        s.departments()

    ::
    '''
    _itemclass = DepartmentObject
    _jsonrpc_method = 'getDepartments'


class HolidayObject(ListItem):
    '''Represents a single holiday.
    '''

    @lazyproperty
    def start(self):
        '''The start date of the holiday, as a datetime object.'''
        return datetime_utils.parse_date(self._data['startDate'])

    @lazyproperty
    def end(self):
        '''The end of the holiday'''
        return datetime_utils.parse_date(self._data['endDate'])

    @lazyproperty
    def name(self):
        '''Name, such as *Nationalfeiertag*.'''
        return self._data['longName']

    @lazyproperty
    def short_name(self):
        '''Abbreviated form of the name'''
        return self._data['name']


class HolidayList(ListResult):
    '''A list of all holidays::

        s.holidays()

    ::
    '''
    _itemclass = HolidayObject
    _jsonrpc_method = 'getHolidays'


class KlassenObject(ListItem):
    '''Represents a school class.'''

    @lazyproperty
    def name(self):
        '''Name of class'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name of class'''
        return self._data['longName']


class KlassenList(ListResult):
    '''A list of all school classes.

    :param schoolyear:
        The schoolyear where we should get all our school \
        classes from. Either a \
        :py:class:`SchoolyearObject` or an \
        id of it.

    ::

        s.klassen()

        year = s.schoolyears().filter(id=2)
        s.klassen(schoolyear=year)

    '''
    _itemclass = KlassenObject
    _jsonrpc_method = 'getKlassen'

    def _jsonrpc_parameters(self, schoolyear=None):
        jsonrpc_parameters = {}
        if schoolyear:
            jsonrpc_parameters.update({
                'schoolyearId': int(schoolyear)
            })

        return jsonrpc_parameters


class PeriodObject(ListItem):
    '''Represents a time range, where lessons/subjects may be held.
    '''

    @lazyproperty
    def start(self):
        '''The start date/time of the period, as datetime object.'''

        return datetime_utils.parse_datetime(
            self._data['date'],
            self._data['startTime']
        )

    @lazyproperty
    def end(self):
        '''The end date/time of the period.'''

        return datetime_utils.parse_datetime(
            self._data['date'],
            self._data['endTime']
        )

    @lazyproperty
    def klassen(self):
        '''A list of :py:class:`KlassenObject` instances,
        which are attending this period.'''

        return self._session.klassen().filter(
            id=set([kl['id'] for kl in self._data['kl']])
        )

    @lazyproperty
    def teachers(self):
        '''A list of :py:class:`TeacherObject` instances,
        which are attending this period.'''

        return self._session.teachers().filter(
            id=set([te['id'] for te in self._data['te']])
        )

    @lazyproperty
    def subjects(self):
        '''A list of :py:class:`SubjectObject` instances,
        which are topic of this period. This is not used for things like
        multiple language lessons (*e.g.* Latin, Spanish, French) -- each of
        those will get placed in their own period.'''

        return self._session.subjects().filter(
            id=set([su['id'] for su in self._data['su']])
        )

    @lazyproperty
    def rooms(self):
        '''The rooms where this period is taking place at. This also is not
        used for multiple lessons, but rather for a single lesson that is
        actually occuring at multiple locations.'''

        return self._session.rooms().filter(
            id=set([ro['id'] for ro in self._data['ro']])
        )

    @lazyproperty
    def code(self):
        '''May be:

          - ``None`` -- There's nothing special about this period.
          - ``"cancelled"`` -- Cancelled
          - ``"irregular"`` -- Substitution/"Supplierung"/Not planned event
        '''

        if 'code' not in self._data:
            return None
        else:
            return self._data['code'] or None

    @lazyproperty
    def type(self):
        '''
        May be:

          - ``"ls"`` -- Normal lesson
          - ``"oh"`` -- Office hour
          - ``"sb"`` -- Standby
          - ``"bs"`` -- Break Supervision
          - ``"ex"`` -- Examination
        '''

        return (self._data['lstype'] if 'lstype' in self._data else 'ls')


class PeriodList(ListResult):
    '''
    Aka timetable

    :param start: a starting date either in the form YYMMDD or as date/time
        object.
    :param end: a ending date in the same form as the starting date.

    Furthermore you have to explicitly define a klasse, teacher, subject, room
    or student parameter containing the id or the object of the thing you want
    to get a timetable about::

        schoolclass = s.klassen().filter(id=1)[0]  # schoolclass #1

        s.timetable(klasse=schoolclass)  # which is the same as...
        s.periods(klasse=schoolclass)

    :raises: :py:class:`builtins.ValueError` -- if something was wrong with the
        arguments supplied.
    '''
    _itemclass = PeriodObject
    _jsonrpc_method = 'getTimetable'

    def to_table(self, *args, **kwargs):
        '''A shortcut for :py:func:`webuntis.utils.timetable_utils.table`.
        Given arguments will be passed to that function.
        '''

        return timetable_utils.table(self, *args, **kwargs)

    def _jsonrpc_parameters(self, start=None, end=None, **type_and_id):
        element_type_table = {
            'klasse':  1,
            'teacher': 2,
            'subject': 3,
            'room':    4,
            'student': 5
        }

        invalid_type_error = TypeError(
            'You have to specify exactly one of the following parameters by '
            'keyword: ' +
            (', '.join(element_type_table.keys()))
        )

        if len(type_and_id) != 1:
            raise invalid_type_error

        element_type, element_id = list(type_and_id.items())[0]

        if element_type not in element_type_table:
            raise invalid_type_error

        # apply end to start and vice-versa if one of them is missing
        if not start and end:
            start = end
        elif not end and start:
            end = start

        # if we have to deal with an object in element_id,
        # its id gets placed here anyway
        parameters = {
            'id': int(element_id),
            'type': element_type_table[element_type],
        }

        if start:
            parameters['startDate'] = datetime_utils.format_date(start)
        if end:
            parameters['endDate'] = datetime_utils.format_date(end)

        return parameters


class RoomObject(ListItem):
    '''Represents a physical room. Such as a classroom, but also the physics
    laboratory or whatever.
    '''
    @lazyproperty
    def name(self):
        '''The short name of the room. Such as PHY.'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''The long name of the room. Such as "Physics lab".'''
        return self._data['longName']


class RoomList(ListResult):
    '''
    Represents a list of rooms::

        s.rooms()

    '''
    _itemclass = RoomObject
    _jsonrpc_method = 'getRooms'


class SchoolyearObject(ListItem):
    '''Represents a schoolyear.
    '''

    @lazyproperty
    def name(self):
        '''"2010/2011"'''

        return self._data['name']

    @lazyproperty
    def start(self):
        '''The start date of the schoolyear, as datetime object'''
        return datetime_utils.parse_date(self._data['startDate'])

    @lazyproperty
    def end(self):
        '''The end date'''
        return datetime_utils.parse_date(self._data['endDate'])

    @lazyproperty
    def is_current(self):
        '''
        Boolean, check if this is the current schoolyear::

            >>> y = s.schoolyears()
            >>> y.current.id
            7
            >>> y.current.is_current
            True
            >>> y.filter(id=y.current.id).is_current
            True

        '''
        return (self == self._parent.current)


class SchoolyearList(ListResult):
    '''
    Represents a list of school years::

        s.schoolyears()

    '''
    _itemclass = SchoolyearObject
    _jsonrpc_method = 'getSchoolyears'

    @lazyproperty
    def current(self):
        '''Returns the current schoolyear in form of a
        :py:class:`SchoolyearObject`'''
        current_data = self._session._request('getCurrentSchoolyear')
        current = self.filter(id=current_data['id'])[0]
        return current


class SubjectObject(ListItem):
    '''Represents a subject.
    '''

    @lazyproperty
    def name(self):
        '''Short name of subject, such as *PHY*'''
        return self._data['name']

    @lazyproperty
    def long_name(self):
        '''Long name of subject, such as *Physics*'''
        return self._data['longName']


class SubjectList(ListResult):
    '''Represents a list of subjects::

        s.subjects()

    ::
    '''
    _itemclass = SubjectObject
    _jsonrpc_method = 'getSubjects'


class TeacherObject(ListItem):
    '''Represents a teacher.
    '''
    @lazyproperty
    def fore_name(self):
        '''fore name of the teacher'''
        return self._data['foreName']

    @lazyproperty
    def long_name(self):
        '''surname of teacher'''
        return self._data['longName']

    surname = long_name

    @lazyproperty
    def name(self):
        '''full name of the teacher'''
        return self._data['name']


class TeacherList(ListResult):
    '''
    Represents a list of teachers::

        s.teachers()  # get all teachers of school

    ::
    '''
    _itemclass = TeacherObject
    _jsonrpc_method = 'getTeachers'


class TimeunitObject(ListItem):
    '''A bunch of timeunits for a specific day.
    '''

    @lazyproperty
    def times(self):
        '''A list of tuples containing the start and the end of each timeunit
        as datetime '''

        return [
            (
                datetime_utils.parse_time(unit['startTime']),
                datetime_utils.parse_time(unit['endTime'])
            ) for unit in self._data['timeUnits']
        ]

    @lazyproperty
    def day(self):
        '''The day the timeunit list is for'''
        return self._data['day']


class TimeunitList(ListResult):
    '''A list of times and dates for the current week. Doesn't contain actual
    data, but is useful when you want to generate a timetable::

        >>> grid = s.timegrid()
        >>>
        >>> # 1 = Sunday
        >>> # 2 = Monday
        >>> # ...
        >>> # 7 = Saturday
        >>> grid[0].day
        2
        >>> grid[0].times
        [
            (datetime.datetime(...), datetime.datetime(...)),
            ...
        ]

    .. note::
        The date-specific properties of the datetime objects are invalid, since
        these are not provided by the official API.
        it.
    '''

    _itemclass = TimeunitObject
    _jsonrpc_method = 'getTimegridUnits'


class ColorInfo(object):
    '''
    An object containing information about a lesson type or a period code::

        >>> lstype = s.statusdata().lesson_types[ls]
        >>> lstype.name
        'ls'
        >>> lstype.forecolor
        '000000'
        >>> lstype.backcolor
        'ee7f00'

    '''

    def __init__(self, session, parent, data):
        self._session = session
        self._parent = parent
        self._data = data

    @lazyproperty
    def name(self):
        '''The name of the LessonType or PeriodCode'''
        return list(self._data.items())[0][0]

    @lazyproperty
    def forecolor(self):
        '''The foreground color used in the web interfacei and elsewhere'''
        return self._data[self.name]['foreColor']

    @lazyproperty
    def backcolor(self):
        '''The background color used in the web interface and elsewhere'''
        return self._data[self.name]['backColor']


class StatusData(Result):
    '''
    Information about lesson types and period codes and their colors::

        s.statusdata()

    '''
    _jsonrpc_method = 'getStatusData'

    @lazyproperty
    def lesson_types(self):
        '''A list of :py:class:`ColorInfo` objects, containing
        information about all lesson types defined'''
        return [
            ColorInfo(self._session, self, data)
            for data in self._data['lstypes']
        ]

    @lazyproperty
    def period_codes(self):
        '''A list of :py:class:`ColorInfo` objects, containing
        information about all period codes defined'''
        return [
            ColorInfo(self._session, self, data)
            for data in self._data['codes']
        ]

# Defines result classes that are accessible from outside
result_objects = {
    'departments': DepartmentList,
    'holidays': HolidayList,
    'klassen': KlassenList,
    'rooms': RoomList,
    'schoolyears': SchoolyearList,
    'subjects': SubjectList,
    'teachers': TeacherList,

    'timegrid': TimeunitList,
    'timeunits': TimeunitList,
    'statusdata': StatusData,

    'timetable': PeriodList,
    'periods': PeriodList
}
