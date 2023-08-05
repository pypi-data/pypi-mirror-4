'''
    This file is part of python-webuntis

    :copyright: (c) 2012 by Markus Unterwaditzer.
    :license: BSD, see LICENSE for more details.
'''
from __future__ import unicode_literals

import mock
import webuntis
import webuntis.utils as utils
import datetime

from webuntis.tests.utils import OfflineTestCase, mock_results, \
    get_json_resource


class BasicUsageTests(OfflineTestCase):
    '''Mock the _get_data method of all result objects and test the package
    against basic usage.'''

    def test_getdepartments_mock(self):
        jsonstr = get_json_resource('getdepartments_mock.json')

        class methods(object):
            @staticmethod
            def getDepartments(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for dep_raw, dep in zip(jsonstr, self.session.departments()):
                self.assertEqual(dep_raw['id'], dep.id)
                self.assertEqual(dep_raw['longName'], dep.long_name)
                self.assertEqual(dep_raw['name'], dep.name)

    def test_getholidays_mock(self):
        jsonstr = get_json_resource('getholidays_mock.json')

        class methods(object):
            @staticmethod
            def getHolidays(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for holiday_raw, holiday in zip(jsonstr, self.session.holidays()):
                self.assertEqual(holiday_raw['id'], holiday.id)
                self.assertEqual(holiday_raw['name'], holiday.short_name)
                self.assertEqual(holiday_raw['longName'], holiday.name)

                self.assertEqual(
                    holiday_raw['startDate'],
                    int(holiday.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    holiday_raw['endDate'],
                    int(holiday.end.strftime('%Y%m%d'))
                )

    def test_getklassen_mock(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        class methods(object):
            @staticmethod
            def getKlassen(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            klassen = self.session.klassen()
            for klasse_raw, klasse in zip(jsonstr, klassen):
                self.assertEqual(klasse_raw['id'], klasse.id)
                self.assertEqual(klasse_raw['name'], klasse.name)
                self.assertEqual(klasse_raw['longName'], klasse.long_name)

            self.assertEqual(klassen.filter(id=129)[0].id, 129)
            self.assertEqual(
                [129, 130, 137],
                sorted(
                    kl.id for kl in
                    klassen.filter(id=set([129, 130, 137]))
                )
            )

            self.assertTrue({'id': 129} in klassen)
            self.assertTrue({'name': '6A'} in klassen)

    def test_gettimetables_mock(self):
        jsonstr = get_json_resource('gettimetables_mock.json')
        jsonstr_kl = get_json_resource('getklassen_mock.json')
        jsonstr_te = get_json_resource('getteachers_mock.json')
        jsonstr_su = get_json_resource('getsubjects_mock.json')
        jsonstr_ro = get_json_resource('getrooms_mock.json')

        class methods(object):
            @staticmethod
            def getTimetable(self, url, jsondata, headers):
                return {'result': jsonstr}

            @staticmethod
            def getKlassen(self, url, jsondata, headers):
                return {'result': jsonstr_kl}

            @staticmethod
            def getTeachers(self, url, jsondata, headers):
                return {'result': jsonstr_te}

            @staticmethod
            def getSubjects(self, url, jsondata, headers):
                return {'result': jsonstr_su}

            @staticmethod
            def getRooms(self, url, jsondata, headers):
                return {'result': jsonstr_ro}

        with mock_results(methods):
            tt = self.session.timetable(klasse=114)

            for period_raw, period in zip(jsonstr, tt):
                self.assertEqual(
                    int(period.start.strftime('%H%M')),
                    period_raw['startTime']
                )
                self.assertEqual(
                    int(period.start.strftime('%Y%m%d')),
                    period_raw['date']
                )

                self.assertEqual(
                    int(period.end.strftime('%H%M')),
                    period_raw['endTime']
                )
                self.assertEqual(
                    int(period.end.strftime('%H%M')),
                    period_raw['endTime']
                )
                if 'code' in period_raw:
                    self.assertEqual(period_raw['code'], period.code)
                else:
                    self.assertEqual(period.code, None)

                if 'type' in period_raw:
                    self.assertEqual(period_raw['lstype'], period.type)
                else:
                    self.assertEqual(period.type, 'ls')

                self.assertEqual(len(period_raw['kl']), len(period.klassen))
                for klasse_raw, klasse in zip(period_raw['kl'], period.klassen):
                    self.assertEqual(klasse.id, klasse_raw['id'])

                self.assertEqual(len(period_raw['te']), len(period.teachers))
                for teacher_raw, teacher in zip(period_raw['te'], period.teachers):
                    self.assertEqual(teacher.id, teacher_raw['id'])

                self.assertEqual(len(period_raw['su']), len(period.subjects))
                for subject_raw, subject in zip(period_raw['su'], period.subjects):
                    self.assertEqual(subject.id, subject_raw['id'])

                self.assertEqual(len(period_raw['ro']), len(period.rooms))
                for room_raw, room in zip(period_raw['ro'], period.rooms):
                    self.assertEqual(room.id, room_raw['id'])

    def test_getrooms_mock(self):
        jsonstr = get_json_resource('getrooms_mock.json')

        class methods(object):
            @staticmethod
            def getRooms(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for room_raw, room in zip(jsonstr, self.session.rooms()):
                self.assertEqual(room_raw['longName'], room.long_name)
                self.assertEqual(room_raw['name'], room.name)
                self.assertEqual(room_raw['id'], room.id)

    def test_getschoolyears_mock(self):
        jsonstr = get_json_resource('getschoolyears_mock.json')
        current_json = jsonstr[3]

        class methods(object):
            @staticmethod
            def getSchoolyears(self, url, jsondata, headers):
                return {'result': jsonstr}

            @staticmethod
            def getCurrentSchoolyear(self, url, jsondata, headers):
                return {'result': current_json}

        with mock_results(methods):
            schoolyears = self.session.schoolyears()

            self.assertEqual(current_json['id'], schoolyears.current.id)
            self.assertTrue(schoolyears.current.is_current)
            current_count = 0
            for year_raw, year in zip(jsonstr, schoolyears):
                self.assertEqual(year_raw['id'], year.id)
                self.assertEqual(year_raw['name'], year.name)

                self.assertEqual(
                    year_raw['startDate'],
                    int(year.start.strftime('%Y%m%d'))
                )
                self.assertEqual(
                    year_raw['endDate'],
                    int(year.end.strftime('%Y%m%d'))
                )
                if year.is_current:
                    self.assertEqual(year, schoolyears.current)
                    current_count += 1
                    self.assertEqual(current_count, 1)

    def test_getsubjects_mock(self):
        jsonstr = get_json_resource('getsubjects_mock.json')

        class methods(object):
            @staticmethod
            def getSubjects(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for subj_raw, subj in zip(jsonstr, self.session.subjects()):
                self.assertEqual(subj_raw['id'], subj.id)
                self.assertEqual(subj_raw['name'], subj.name)
                self.assertEqual(subj_raw['longName'], subj.long_name)

    def test_getteachers_mock(self):
        jsonstr = get_json_resource('getteachers_mock.json')

        class methods(object):
            @staticmethod
            def getTeachers(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for t_raw, t in zip(jsonstr, self.session.teachers()):
                self.assertEqual(t_raw['longName'], t.long_name)
                self.assertEqual(t_raw['longName'], t.surname)
                self.assertEqual(t_raw['foreName'], t.fore_name)
                self.assertEqual(t_raw['name'], t.name)

    def test_gettimegrid_mock(self):
        jsonstr = get_json_resource('gettimegrid_mock.json')

        class methods(object):
            @staticmethod
            def getTimegridUnits(self, url, jsondata, headers):
                return {'result': jsonstr}

        with mock_results(methods):
            for t_raw, t in zip(jsonstr, self.session.timegrid()):
                self.assertEqual(t_raw['day'], t.day)
                for t2_raw, t2 in zip(t_raw['timeUnits'], t.times):
                    self.assertEqual(t2_raw['startTime'],
                                     int(t2[0].strftime('%H%M')))
                    self.assertEqual(t2_raw['endTime'],
                                     int(t2[1].strftime('%H%M')))

    def test_getstatusdata_mock(self):
        jsonstr = get_json_resource('getstatusdata_mock.json')

        class methods(object):
            @staticmethod
            def getStatusData(self, url, jsondata, headers):
                return {'result': jsonstr}

        def validate_statusdata(raw, processed):
            name = list(raw.items())[0][0]
            colors = raw[name]
            self.assertEqual(name, processed.name)
            self.assertEqual(colors['foreColor'], processed.forecolor)
            self.assertEqual(colors['backColor'], processed.backcolor)

        with mock_results(methods):
            statusdata = self.session.statusdata()
            for lstype_raw, lstype in zip(jsonstr['lstypes'],
                                          statusdata.lesson_types):
                validate_statusdata(lstype_raw, lstype)


            for code_raw, code in zip(jsonstr['codes'], statusdata.period_codes):
                validate_statusdata(code_raw, code)
                

    def test_login_repeat_invalid_session(self):
        retry_amount = 5
        calls = []

        # This produces a list of 5 * ['getCurrentSchoolyear'] with ['logout',
        # 'authenticate'] between each.
        expected_calls = (
            ['getCurrentSchoolyear', 'logout', 'authenticate']
            * (retry_amount + 1)
        )[:-2]

        class methods(object):
            @staticmethod
            def authenticate(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
                }

            @staticmethod
            def getCurrentSchoolyear(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'error': {'code': -8520, 'message': 'Not Logged In!'}
                }

            @staticmethod
            def logout(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'result': {'bla': 'blub'}
                }

        with mock_results(methods):
            with mock.patch.dict(
                self.session.options,
                {'login_repeat': retry_amount}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  self.session._request, 'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)

    def test_login_repeat_not_logged_in(self):
        retry_amount = 1
        calls = []

        # This produces a list of 5 * ['getCurrentSchoolyear'] with ['logout',
        # 'authenticate'] between each.
        expected_calls = ['authenticate', 'getCurrentSchoolyear']

        class methods(object):
            @staticmethod
            def authenticate(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'id': jsondata['id'],
                    'result': {'sessionId': 'Foobar_session_' + jsondata['id']}
                }

            @staticmethod
            def _nope(self, url, jsondata, headers):
                calls.append(jsondata['method'])
                return {
                    'id': jsondata['id'],
                    'error': {'code': -8520, 'message': 'Not Logged In!'}
                }

            getCurrentSchoolyear = logout = _nope
            del _nope

        with mock_results(methods):
            with mock.patch.dict(
                self.session.options,
                {'login_repeat': retry_amount, 'jsessionid': None}
            ):
                self.assertRaises(webuntis.errors.NotLoggedInError,
                                  self.session._request, 'getCurrentSchoolyear')

        self.assertEqual(calls, expected_calls)


class InternalTests(OfflineTestCase):
    '''Test certain internal interfaces, such as utils'''

    def test_make_cache_key(self):
        # The hash builtin will take care of us if the results aren't hashable.
        hash(self.session._make_cache_key('getStuff', {'foo': 'bar'}))
        hash(self.session._make_cache_key('getStuff', {}))
        hash(self.session._make_cache_key('getStuff', None))

    def test_is_iterable_util(self):
        tests = [
            ((), True),
            (None, False),
            ([], True),
            ({}, True),
            ("FOO", False),
            (str("FOO"), False),
            (123, False)
        ]

        for given_input, expected_output in tests:
            self.assertEqual(utils.is_iterable(given_input), expected_output)

    def test_options_invalidattribute(self):
        self.assertFalse('nigglywiggly' in self.session.options)
        self.assertRaises(
            KeyError,
            self.session.options.__getitem__,
            'nigglywiggly'
        )

    def test_datetime_utils(self):
        obj = utils.datetime_utils.parse_datetime(20121005, 0)
        self.assertEqual(obj.year, 2012)
        self.assertEqual(obj.month, 10)
        self.assertEqual(obj.day, 5)
        self.assertEqual(obj.hour, 0)
        self.assertEqual(obj.minute, 0)
        self.assertEqual(obj.second, 0)

    def test_filterdict(self):
        store = utils.FilterDict({
            'whatever': lambda x: x,
            'always_whoop': lambda x: 'whoop'
        })
        store['whatever'] = 'lel'
        self.assertEqual(store['whatever'], 'lel')

        store['always_whoop'] = 'what'
        self.assertEqual(store['always_whoop'], 'whoop')

        del store['whatever']
        self.assertRaises(KeyError, store.__getitem__, 'whatever')

        del store['always_whoop']
        self.assertRaises(KeyError, store.__getitem__, 'always_whoop')

    def test_session_invalidattribute(self):
        self.assertRaises(AttributeError, getattr, self.session, 'foobar')
        self.assertFalse(hasattr(self.session, 'foobar'))

    def test_requestcaching(self):
        jsonstr = get_json_resource('getklassen_mock.json')

        def result_mock(s, method, params=None, use_login_repeat=None):
            self.assertEqual(method, 'getKlassen')
            return jsonstr

        with mock.patch(
            'webuntis.session.Session._request',
            new=result_mock
        ):
            self.session.klassen()

        with mock.patch(
            'webuntis.session.Session._request',
            side_effect=Exception('CHUCK TESTA')
        ):
            self.session.klassen()

    def test_listitem(self):
        session = self.session
        parent = None
        data = {'id': 42}
        item = webuntis.objects.ListItem(session=session, parent=parent, data=data)

        self.assertEqual(item._session, session)
        self.assertEqual(item._parent, parent)
        self.assertEqual(item._data, data)
        self.assertEqual(item.id, data['id'])
        self.assertEqual(int(item), item.id)

    def test_result_object_without_parameters_method(self):
        with mock.patch.object(
            webuntis.objects.Result,
            '_jsonrpc_parameters',
            new=False
        ):
            obj = webuntis.objects.Result(session=self.session, kwargs={})
            self.assertRaises(NotImplementedError, obj.get_data)

    def test_optionparsers_server(self):
        tests = [
            ('webuntis.grupet.at',
                'http://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('https://webuntis.grupet.at',
                'https://webuntis.grupet.at/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at:8080',
                'http://webuntis.grupet.at:8080/WebUntis/jsonrpc.do'),
            ('webuntis.grupet.at/a/b/c', 'http://webuntis.grupet.at/a/b/c'),
            ('webuntis.grupet.at/', 'http://webuntis.grupet.at/'),
        ]

        for parser_input, expected_output in tests:
            self.assertEqual(
                webuntis.utils.option_utils.server(parser_input),
                expected_output
            )

        self.assertRaises(ValueError,
                          webuntis.utils.option_utils.server, '!"$%')

    def test_resultobject_get_data(self):
        kwargs = {}
        testclass = webuntis.objects.DepartmentList
        testobj = testclass(session=self.session, kwargs=kwargs)

        class methods(object):
            @staticmethod
            def getDepartments(req, url, jsondata, headers):
                self.assertEqual(jsondata['params'],
                                 testobj._jsonrpc_parameters(**kwargs))
                return {'result': {}}

        with mock_results(methods):
            testobj.get_data()

    def helper_jsonrpc_parameters(self, resultclass):
        '''A wrapper for the _jsonrpc_parameters method of any result-type
        class.'''
        def jsonrpc_parameters(kwargs):
            return resultclass(
                session=self.session,
                kwargs={}
            )._jsonrpc_parameters(
                **kwargs
            )

        return jsonrpc_parameters

    def test_objects_klassenlist_jsonrpc_parameters(self):
        tests = [
            ({'schoolyear': 13}, {'schoolyearId': 13}),
            ({'schoolyear': "123"}, {'schoolyearId': 123})
        ]

        for given_input, expected_output in tests:
            self.assertEqual(
                self.helper_jsonrpc_parameters(webuntis.objects.KlassenList)(given_input),
                expected_output
            )

    def test_objects_periodlist_jsonrpc_parameters(self):
        parambuilder = self.helper_jsonrpc_parameters(webuntis.objects.PeriodList)
        dtobj = datetime.datetime.now()
        dtobj_formatted = int(dtobj.strftime('%Y%m%d'))
        tests = [
            ({'start': None, 'end': None, 'klasse': 123},
                {'id': 123, 'type': 1}),
            ({'start': None, 'end': None, 'teacher': 124},
                {'id': 124, 'type': 2}),
            ({'start': None, 'end': None, 'subject': 154},
                {'id': 154, 'type': 3}),
            ({'start': None, 'end': dtobj, 'subject': 1337},
                {
                    'id': 1337,
                    'type': 3,
                    'startDate': dtobj_formatted,
                    'endDate': dtobj_formatted
                }),
            ({'end': None, 'start': dtobj, 'subject': 1337},
                {
                    'id': 1337,
                    'type': 3,
                    'startDate': dtobj_formatted,
                    'endDate': dtobj_formatted
                })
        ]
        for given_input, expected_output in tests:
            self.assertEqual(
                parambuilder(given_input),
                expected_output
            )

        self.assertRaises(TypeError, parambuilder, {})
        self.assertRaises(TypeError, parambuilder, {'foobar': 123})

    def test_resultclass_invalid_arguments(self):
        self.assertRaises(TypeError, webuntis.objects.Result, session=self.session, kwargs={}, data="LELELE")
        self.assertRaises(TypeError, webuntis.objects.Result)
        self.assertRaises(TypeError, webuntis.objects.Result, session=self.session)
