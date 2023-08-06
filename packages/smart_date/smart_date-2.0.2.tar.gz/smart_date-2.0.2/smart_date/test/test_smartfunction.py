# -*- coding: utf-8 -*-
# pylint: disable=C0302, E0211, R0201
from unittest import TestCase
import smart_date.date as date
from smart_date.test.data_provider import data_provider
from smart_date.smartfunction import FullFormula, EnumFormula, \
    DiapasonFormula, SmartFormula, BlasFormula, BlasYearFormula, \
    SimpleDateFormula, FormulaException, Formula, smart_function


class FormulaTest(TestCase):
    def test_sort_dates_list(self):
        # просто фейк-формула
        formula_obj = Formula('xxx')
        formula_obj.dates_list = [
            (1, 1, 1984), (1, 12, 1983), (3, 11, 1983),
            (5, 11, 1983), (10, 1, 1983), (1, 2, 1983),
            (11, 9, 1982)
        ]
        formula_obj.sort_dates_list()
        self.assertEquals(
            formula_obj.dates_list,
            [
                (11, 9, 1982), (10, 1, 1983), (1, 2, 1983),
                (3, 11, 1983), (5, 11, 1983), (1, 12, 1983),
                (1, 1, 1984),
            ],
            'получилось: {0}'.format(formula_obj.dates_list)
        )


class FullFormulaTest(TestCase):
    def provider_explain():
        return (
            ("12.01,12.15.01~[12<{Pascha}~18<{Pascha}||1]"
             ",[{be}|1000000]|1100111|1,2,3",
             '1100111', '1,2,3',
             '12.01,12.15.01~[12<{Pascha}~18<{Pascha}||1],[{be}|1000000]'),
            ('12.01~[12.02~13.04|100000]|1100001',
             '1100001', '0', '12.01~[12.02~13.04|100000]'),
            ('19.01|1111111', '1111111', '0', '19.01'),
            ('19.01||0', '1111111', '0', '19.01'),
            ('12.01~[12.02~13.04|100000]', '1111111', '0',
             '12.01~[12.02~13.04|100000]'),
            ('19.01', '1111111', '0', '19.01'),
        )

    @data_provider(provider_explain)
    def test_explain(self, full_formula, w_filter, d_filter, formula):
        frm, w_f, d_f = FullFormula.explain(full_formula)
        self.assertEquals(
            frm, formula,
            'в полной формуле {0} формула '
            'должна выйти {1}, но не {2}'.format(full_formula, formula, frm)
        )
        self.assertEquals(
            w_f, w_filter, 'в полной формуле {0} фильтр дней '
                           'должен выйти {1}, но не {2}'
                           .format(full_formula, w_filter, w_f)
        )
        self.assertEquals(
            d_f, d_filter, 'в полной формуле {0} фильтр данных '
                           'должен выйти {1}, но не {2}'
                           .format(full_formula, d_filter, d_f)
        )

    def provider_check():
        return (
            ('11.01|1|1|1', False),
            ('11.01|1|1', False),
            ('11.01||1,,2', False),
            ('11.01||1,--2', False),
            ('11.01|1111112|1', False),
            ('11.01|1111111|1', True),
            ('11.01|1111111|-1,1', True),
            ('11.01|1111111|', True),
            ('11.01|1111111|11,12', True),
            ('11.01||0', True),

        )

    @data_provider(provider_check)
    def test_check(self, formula, correct):
        try:
            formula_obj = FullFormula(formula)
            formula_obj.check(*FullFormula.explain(formula))
            is_correct = True
        except FormulaException:
            is_correct = False
        self.assertEquals(is_correct, correct)

    def provider_week_filter():
        return (
            (
                '1111111',
                [(1, 11, 1983), (2, 11, 1983), (3, 11, 1983)],
                [(1, 11, 1983), (2, 11, 1983), (3, 11, 1983)]
            ),
            (
                '0000000',
                [(1, 11, 1983), (2, 11, 1983), (3, 11, 1983)],
                []
            ),
            (
                '1010100',
                [
                    (19, 11, 2012), (20, 11, 2012), (21, 11, 2012),
                    (22, 11, 2012), (23, 11, 2012), (24, 11, 2012),
                    (25, 11, 2012)
                ],
                [
                    (19, 11, 2012), (21, 11, 2012), (23, 11, 2012)
                ],
            ),
            (
                '0000011',
                [
                    (19, 11, 2012), (20, 11, 2012), (21, 11, 2012),
                    (22, 11, 2012), (23, 11, 2012), (24, 11, 2012),
                    (25, 11, 2012), (26, 11, 2012), (27, 11, 2012),
                    (28, 11, 2012), (29, 11, 2012), (30, 11, 2012),
                    (1, 12, 2012), (2, 12, 2012)
                ],
                [
                    (24, 11, 2012), (25, 11, 2012), (1, 12, 2012),
                    (2, 12, 2012)
                ],
            )
        )

    @data_provider(provider_week_filter)
    def test_week_filter(self, w_filter, dates_list, result_dates_list):
        # инициируем объект FullFormula с фильтром.
        # сама формула не важна, потому как список дат мы ниже внедрим
        formula_obj = FullFormula('xxx')
        # внедрим список дат
        formula_obj.dates_list = dates_list
        formula_obj.week_filter(w_filter)
        self.assertEquals(
            result_dates_list, formula_obj.dates_list,
            'для фильтра {0} результат не верный. Получился {1}'.format(
                w_filter, formula_obj.dates_list
            )
        )

    def provider_data_filter():
        def week_dates():
            return [
                (19, 11, 2012), (20, 11, 2012), (21, 11, 2012),
                (22, 11, 2012), (23, 11, 2012), (24, 11, 2012),
                (25, 11, 2012)
            ]
        return (
            ('0,1,2,3', week_dates(), week_dates()),
            ('1', week_dates(), [(19, 11, 2012)]),
            ('1,2', week_dates(), [(19, 11, 2012), (20, 11, 2012)]),
            ('-1,2', week_dates(), [(20, 11, 2012), (25, 11, 2012)]),
        )

    @data_provider(provider_data_filter)
    def test_data_filter(self, d_filter, dates_list, result_dates_list):
        #аналогично test_week_filter
        formula_obj = FullFormula('xxx')
        formula_obj.dates_list = dates_list
        formula_obj.data_filter(d_filter)
        self.assertEquals(result_dates_list, formula_obj.dates_list)

    def provider_generatelist():
        return (
            (
                '[29.10~4.11|0000011]', 2012,
                [(3, 11, 2012), (4, 11, 2012)]
            ),
            (
                '29.10~4.11|0100011|1,2', 2012,
                [
                    (30, 10, 2012), (3, 11, 2012)
                ]
            ),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = FullFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class EnumFormulaTest(TestCase):
    def provider_explain():
        return (
            ('12.11,[11.02,[12.02]|1000000|1,2],15.01~14.05,'
             ' [11.04~15,11.14|1000000|1,4],14.05',
             ['12.11', '[11.02,[12.02]|1000000|1,2]',
              '15.01~14.05', '[11.04~15,11.14|1000000|1,4]', '14.05']),
            ('11.11', ['11.11']),
            ('11.11~[11.11||1,2]', ['11.11~[11.11||1,2]']),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, f_list):
        self.assertEquals(EnumFormula.explain(formula), f_list)

    def provider_is_formula():
        return (
            ('11.11,12.11', True),
            ('11.11~[12.11,12.11]', False),
            ('[12.11,12.11]~[12,12||1,2]', False),
            ('[12.11,12.11]~[12,12||1,2],11.12', True),
            ('11.11~12.11~13.11', False),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        self.assertEquals(EnumFormula.is_formula(formula), result)

    def provider_generatelist():
        c_year = date.get_current_year()
        return (
            (
                '12.01,14.01', 2010,
                [(12, 1, 2010), (14, 1, 2010)]
            ),
            (
                '[30.01~3.02],5.02', 2010,
                [
                    (30, 1, 2010), (31, 1, 2010), (1, 2, 2010),
                    (2, 2, 2010), (3, 2, 2010), (5, 2, 2010)
                ]
            ),
            (
                '{b},3.01', None,
                [
                    (1, 1, c_year), (3, 1, c_year)
                ]
            ),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = EnumFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class DiapasonFormulaTest(TestCase):
    def provider_is_formula():
        return (
            ('11.11,12.11', False),
            ('11.11~[12.11,12.11]', True),
            ('[12.11,12.11]~[12,12||1,2]', True),
            ('11.11~12.11~13.11', False),
            ('11.11~12.11', True),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        self.assertEquals(DiapasonFormula.is_formula(formula), result)

    def provider_explain():
        return (
            ('12>12.01~11.02', ['12>12.01', '11.02']),
            (
                '[11.12~15.12]~[20.12~21.12]',
                ['[11.12~15.12]', '[20.12~21.12]']
            ),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, f_list):
        self.assertEquals(DiapasonFormula.explain(formula), f_list)

    def provider_check():
        return (
            (
                [(1, 11, 1983), (2, 11, 1983)],
                [(3, 11, 1983), (4, 11, 1983)],
                False
            ),
            (
                [(1, 11, 1983)],
                [(3, 11, 1983), (4, 11, 1983)],
                False
            ),
            (
                [(1, 11, 1983), (2, 11, 1983)],
                [(4, 11, 1983)],
                False
            ),
            (
                [(4, 11, 1983)],
                [(3, 11, 1983)],
                False
            ),
            (
                [(3, 11, 1983)],
                [(3, 11, 1983)],
                False
            ),
            (
                [(1, 11, 1983)],
                [(3, 11, 1983)],
                True
            ),
        )

    @data_provider(provider_check)
    def test_check(self, date_list1, date_list2, correct):
        try:
            #просто левая формула
            formula_obj = DiapasonFormula('12.01~13.01')
            formula_obj.check(date_list1, date_list2)
            is_correct = True
        except FormulaException:
            is_correct = False
        self.assertEquals(is_correct, correct)

    def provider_generate_list():
        return (
            (
                (3, 11, 1983), (5, 11, 1983),
                [(3, 11, 1983), (4, 11, 1983), (5, 11, 1983)]
            ),
            (
                (3, 11, 1983), (4, 11, 1983),
                [(3, 11, 1983), (4, 11, 1983)]
            ),
            (
                (29, 11, 1983), (4, 12, 1983),
                [
                    (29, 11, 1983), (30, 11, 1983), (1, 12, 1983),
                    (2, 12, 1983), (3, 12, 1983), (4, 12, 1983)
                ]
            ),
            (
                (26, 2, 2011), (2, 3, 2011),
                [
                    (26, 2, 2011), (27, 2, 2011), (28, 2, 2011),
                    (1, 3, 2011), (2, 3, 2011),
                ]
            ),
            (
                (26, 2, 2000), (2, 3, 2000),
                [
                    (26, 2, 2000), (27, 2, 2000), (28, 2, 2000),
                    (29, 2, 2000), (1, 3, 2000), (2, 3, 2000),
                ]
            ),
        )

    @data_provider(provider_generate_list)
    def test_diapason(self, date1, date2, dates_list):
        #просто левая формула
        formula_obj = DiapasonFormula('12.01~13.01')
        formula_obj.diapason([date1], [date2])
        self.assertEquals(formula_obj.dates_list, dates_list)

    def provider_generatelist():
        c_year = date.get_current_year()
        return (
            (
                '12.01~14.01', 2010,
                [(12, 1, 2010), (13, 1, 2010), (14, 1, 2010)]
            ),
            (
                '30.01~3.02', 2010,
                [
                    (30, 1, 2010), (31, 1, 2010), (1, 2, 2010),
                    (2, 2, 2010), (3, 2, 2010)
                ]
            ),
            (
                '{b}~3.01', None,
                [
                    (1, 1, c_year), (2, 1, c_year), (3, 1, c_year)
                ]
            ),
            (
                '10<11.12~3.12', 2010,
                [(1, 12, 2010), (2, 12, 2010), (3, 12, 2010)]
            ),

        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = DiapasonFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class SmartFormulaTest(TestCase):

    def provider_is_formula():
        return (
            ('{xxx}', True),
            ('{xx(1)}', True),
            ('xx}', False),
            ('{xx)', False),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        self.assertEquals(SmartFormula.is_formula(formula), result)

    def provider_explain():
        return (
            ('{be}', ['be', None]),
            ('{e(1900)}', ['e', '1900']),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, f_list):
        self.assertEquals(SmartFormula.explain(formula), f_list)

    def provider_generatelist():
        return (
            ('{b}', 2010, [(1, 1, 2010)]),
            ('{t}', None, [date.today()]),
            ('{t}', 2010, [date.today()]),
            ('{b(2011)}', 2010, [(1, 1, 2011)]),
            ('{e}', None, [(31, 12, date.get_current_year())]),
            ('{e(2000)}', None, [(31, 12, 2000)]),
            ('{Pascha}', 2000, [date.Pascha(2000)]),
            ('{Pascha}', None, [date.Pascha(date.get_current_year())]),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = SmartFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class BlasFormulaTest(TestCase):
    def provider_is_formula():
        return (
            ('12>{Pascha}', True),
            ('-12>[12>11.02]', True),
            ('12>{Pascha}>11', False),
            ('11.12>11', False),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        message = 'формула {0} должна быть {1}'.format(
            formula,
            'корректной' if result else 'не корректной',
        )
        self.assertEquals(BlasFormula.is_formula(formula), result, message)

    def provider_explain():
        return (
            ('12>{Pascha}', 12, '{Pascha}'),
            ('12<{Pascha}', -12, '{Pascha}'),
            ('-12<[12>11.02]', 12, '[12>11.02]'),
            ('-12>[12>11.02]', -12, '[12>11.02]'),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, days, subformula):
        _days, _subformula = BlasFormula.explain(formula)
        self.assertEquals(days, _days)
        self.assertEquals(subformula, _subformula)

    def provider_generatelist():
        return (
            ('12>11.02', 2010, [(23, 2, 2010)]),
            ('20<11.02.+10', None, [(22, 1, date.get_current_year() + 10)]),
            ('1>28.02', 2000, [(29, 2, 2000)]),
            ('2>28.02', 2000, [(1, 3, 2000)]),
            ('48<{Pascha}', 2012, [(27, 2, 2012)]),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = BlasFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class BlasYearFormulaTest(TestCase):
    def provider_is_formula():
        return (
            ('01.12.+7', True),
            ('15.06.-1', True),
            ('15.06-1', False),
            ('15.06.11', False),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        message = 'формула {0} должна быть {1}'.format(
            formula,
            'корректной' if result else 'не корректной',
        )
        self.assertEquals(BlasYearFormula.is_formula(formula), result, message)

    def provider_explain():
        return (
            ('01.12.+7', '01.12', '+7'),
            ('15.06.-1', '15.06', '-1'),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, subformula, year):
        _subformula, _year = BlasYearFormula.explain(formula)
        self.assertEquals(year, _year)
        self.assertEquals(subformula, _subformula)

    def provider_generatelist():
        return (
            ('11.02.+1', 2010, [(11, 2, 2011)]),
            ('11.02.-2', '2010', [(11, 2, 2008)]),
            ('11.02.+10', None, [(11, 2, date.get_current_year() + 10)]),
            ('29.02.+1', 1999, [(29, 2, 2000)]),
            ('29.02.-1', 2000, False),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = BlasYearFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class SimpleDateFormulaTest(TestCase):
    def provider_is_formula():
        return (
            ('11.01.2011', True),
            ('3.11', True),
            ('3.11.12', False),
            ('3.11.', False),
        )

    @data_provider(provider_is_formula)
    def test_is_formula(self, formula, result):
        message = 'формула {0} должна быть {1}'.format(
            formula,
            'корректной' if result else 'не корректной',
        )
        self.assertEquals(
            SimpleDateFormula.is_formula(formula), result,
            message
        )

    def provider_explain():
        return (
            ('11.01.2011', '11', '01', '2011'),
            ('15.06', '15', '06', '0'),
        )

    @data_provider(provider_explain)
    def test_explain(self, formula, day, month, year):
        self.assertEquals(
            SimpleDateFormula.explain(formula),
            [day, month, year]
        )

    def provider_generatelist():
        return (
            ('11.02', 2010, [(11, 2, 2010)]),
            ('11.02', '2010', [(11, 2, 2010)]),
            ('11.02', None, [(11, 2, date.get_current_year())]),
            ('29.02', 2000, [(29, 2, 2000)]),
            ('29.02', 2001, False),
        )

    @data_provider(provider_generatelist)
    def test_generatelist(self, formula, year, dates_list):
        formula_obj = SimpleDateFormula(formula, year)
        try:
            formula_obj.generatelist()
            d_list = formula_obj.dates_list
        except FormulaException:
            d_list = False
        self.assertEquals(d_list, dates_list)


class SmartFunctionTest(TestCase):
    '''
    очень много проверок :-)
    '''
    def provider_function():
        def get_period(date1, date2):
            list_d = [date1]
            current_date = date1
            while date.date_compare(*current_date + date2) == 1:
                current_date = date.date_shift(*current_date + (1,))
                list_d.append(current_date)
            return list_d

        c_year = date.get_current_year()
        return (
            #simple
            ('12.01', None, [(12, 1, c_year)]),
            ('[12.01]', None, [(12, 1, c_year)]),
            ('[28.03]', None, [(28, 3, c_year)]),
            ('[28.03.2010||]', None, [(28, 3, 2010)]),
            ('[28.03]', 2010, [(28, 3, 2010)]),
            ('[28.12.2010]', None, [(28, 12, 2010)]),
            ('[28.12,29.12]', None, [(28, 12, c_year), (29, 12, c_year)]),
            #посты
            #рождественский пост
            (
                '28.11~06.01.+1', 2010,
                get_period((28, 11, 2010), (6, 1, 2011))
            ),
            (
                '28.11~06.01.+1', 2013,
                get_period((28, 11, 2013), (6, 1, 2014))
            ),
            #  Успенский пост
            (
                '14.08~27.08', 2010,
                get_period((14, 8, 2010), (27, 8, 2010))
            ),
            (
                '14.08~27.08', 2011,
                get_period((14, 8, 2011), (27, 8, 2011))
            ),
            #Петров пост
            (
                '57>{Pascha}~11.07', 2010,
                get_period((31, 5, 2010), (11, 7, 2010))
            ),
            (
                '57>{Pascha}~11.07', 2011,
                get_period((20, 6, 2011), (11, 7, 2011))
            ),
            # Великий пост
            (
                '48<{Pascha}~1<{Pascha}', 2011,
                get_period((7, 3, 2011), (23, 4, 2011))
            ),
            (
                '48<{Pascha}~1<{Pascha}', 2012,
                get_period((27, 2, 2012), (14, 4, 2012))
            ),
            # мясоеды
            #Осенний мясоед
            (
                '28.08~27.11', 2010,
                get_period((28, 8, 2010), (27, 11, 2010))
            ),
            (
                '28.08~27.11', 2011,
                get_period((28, 8, 2011), (27, 11, 2011))
            ),
            (
                '28.08~27.11', 2013,
                get_period((28, 8, 2013), (27, 11, 2013))
            ),
            #  зимний мясоед
            (
                '07.01~49<{Pascha}', 2010,
                get_period((07, 1, 2010), (14, 2, 2010))
            ),
            (
                '07.01~49<{Pascha}', 2011,
                get_period((07, 1, 2011), (6, 3, 2011))
            ),
            (
                '07.01~49<{Pascha}', 2012,
                get_period((7, 1, 2012), (26, 2, 2012))
            ),
            #  Весенний мясоед
            (
                '{Pascha}~56>{Pascha}', 2010,
                get_period((04, 4, 2010), (30, 5, 2010))
            ),
            (
                '{Pascha}~56>{Pascha}', 2011,
                get_period((24, 4, 2011), (19, 6, 2011))
            ),
            (
                '{Pascha}~56>{Pascha}', 2012,
                get_period((15, 4, 2012), (10, 6, 2012))
            ),
            #  Летний мясоед
            (
                '12.07~13.08', 2010,
                get_period((12, 7, 2010), (13, 8, 2010))
            ),
            (
                '12.07~13.08', 2011,
                get_period((12, 7, 2011), (13, 8, 2011))
            ),
            (
                '12.07~13.08', 2012,
                get_period((12, 7, 2012), (13, 8, 2012))
            ),
            #  сплошные седмицы
            #  Святки
            (
                '07.01~18.01', 2011,
                get_period((7, 1, 2011), (18, 1, 2011))
            ),
            (
                '07.01~18.01', 2012,
                get_period((07, 1, 2012), (18, 1, 2012))
            ),
            (
                '07.01~18.01', 2013,
                get_period((07, 1, 2013), (18, 1, 2013))
            ),
            #  седмица Мытаря и фарисея
            (
                '69<{Pascha}~63<{Pascha}', 2011,
                get_period((14, 2, 2011), (20, 2, 2011))
            ),
            (
                '69<{Pascha}~63<{Pascha}', 2012,
                get_period((06, 2, 2012), (12, 2, 2012))
            ),
            (
                '69<{Pascha}~63<{Pascha}', 2013,
                get_period((25, 2, 2013), (03, 3, 2013))
            ),
            #  масленица
            (
                '55<{Pascha}~49<{Pascha}', 2011,
                get_period((28, 2, 2011), (06, 3, 2011))
            ),
            (
                '55<{Pascha}~49<{Pascha}', 2012,
                get_period((20, 2, 2012), (26, 2, 2012))
            ),
            (
                '55<{Pascha}~49<{Pascha}', 2013,
                get_period((11, 3, 2013), (17, 3, 2013))
            ),
            #  Пасхальная седмица
            (
                '{Pascha}~6>{Pascha}', 2011,
                get_period((24, 4, 2011), (30, 4, 2011))
            ),
            (
                '{Pascha}~6>{Pascha}', 2012,
                get_period((15, 4, 2012), (21, 4, 2012))
            ),
            (
                '{Pascha}~6>{Pascha}', 2013,
                get_period((5, 5, 2013), (11, 5, 2013))
            ),
            #Троицкая седмица
            (
                '50>{Pascha}~56>{Pascha}', 2011,
                get_period((13, 6, 2011), (19, 6, 2011))
            ),
            (
                '50>{Pascha}~56>{Pascha}', 2012,
                get_period((04, 6, 2012), (10, 6, 2012))
            ),
            (
                '50>{Pascha}~56>{Pascha}', 2013,
                get_period((24, 6, 2013), (30, 6, 2013))
            ),
            #  мясопустная седмица
            (
                '62<{Pascha}~56<{Pascha}', 2011,
                get_period((21, 2, 2011), (27, 2, 2011))
            ),
            (
                '62<{Pascha}~56<{Pascha}', 2012,
                get_period((13, 2, 2012), (19, 2, 2012))
            ),
            (
                '62<{Pascha}~56<{Pascha}', 2013,
                get_period((04, 3, 2013), (10, 3, 2013))
            ),
            #  Страстная седмица
            (
                '6<{Pascha}~1<{Pascha}', 2011,
                get_period((18, 4, 2011), (23, 4, 2011))
            ),
            (
                '6<{Pascha}~1<{Pascha}', 2012,
                get_period((9, 4, 2012), (14, 4, 2012))
            ),
            (
                '6<{Pascha}~1<{Pascha}', 2013,
                get_period((29, 4, 2013), (04, 5, 2013))
            ),
            #  Страстной понедельик
            ('6<{Pascha}', 2011, [(18, 4, 2011)]),
            #  Страстной вторник
            ('5<{Pascha}', 2011, [(19, 4, 2011)]),
            #  Страстной среда
            ('4<{Pascha}', 2011, [(20, 4, 2011)]),
            #  Страстной четверг
            ('3<{Pascha}', 2011, [(21, 4, 2011)]),
            #  Страстная пятница
            ('2<{Pascha}', 2011, [(22, 4, 2011)]),
            #  Страстная суббота
            ('1<{Pascha}', 2011, [(23, 4, 2011)]),
            #  Великие праздники
            #  пасха
            ('{Pascha}', 2010, [(4, 4, 2010)]),
            ('{Pascha}', 2011, [(24, 4, 2011)]),
            ('{Pascha}', 2012, [(15, 4, 2012)]),
            ('{Pascha}', 2013, [(5, 5, 2013)]),
            ('{Pascha}', 2014, [(20, 4, 2014)]),
            ('{Pascha}', 2015, [(12, 4, 2015)]),
            ('{Pascha}', 2016, [(1, 5, 2016)]),
            ('{Pascha}', 2017, [(16, 4, 2017)]),
            ('{Pascha}', 2018, [(8, 4, 2018)]),
            ('{Pascha}', 2019, [(28, 4, 2019)]),
            ('{Pascha}', 2020, [(19, 4, 2020)]),
            #   Рождество Богородицы
            ('21.09', 2010, [(21, 9, 2010)]),
            ('21.09', 2011, [(21, 9, 2011)]),
            #   Водвижение креста господня
            ('27.09', 2010, [(27, 9, 2010)]),
            ('27.09', 2011, [(27, 9, 2011)]),
            #   Введение во храм Пресвятой Богородицы
            ('04.12', 2010, [(4, 12, 2010)]),
            ('04.12', 2011, [(4, 12, 2011)]),
            #   Рождество христово
            ('07.01', 2010, [(7, 1, 2010)]),
            ('07.01', 2011, [(7, 1, 2011)]),
            #Крещение Господне
            ('19.01', 2010, [(19, 1, 2010)]),
            ('19.01', 2011, [(19, 1, 2011)]),
            #Сретение Господне
            ('15.02', 2010, [(15, 2, 2010)]),
            ('15.02', 2011, [(15, 2, 2011)]),
            #Благовещение Пресвятой Богородицы
            ('07.04', 2010, [(7, 4, 2010)]),
            ('07.04', 2011, [(7, 4, 2011)]),
            #Вход Господень в Иерусалим
            ('7<{Pascha}', 2010, [(28, 3, 2010)]),
            ('7<{Pascha}', 2011, [(17, 4, 2011)]),
            ('7<{Pascha}', 2012, [(8, 4, 2012)]),
            ('7<{Pascha}', 2013, [(28, 4, 2013)]),
            ('7<{Pascha}', 2014, [(13, 4, 2014)]),
            ('7<{Pascha}', 2015, [(5, 4, 2015)]),
            #Вознесение Господне
            ('39>{Pascha}', 2010, [(13, 5, 2010)]),
            ('39>{Pascha}', 2011, [(2, 6, 2011)]),
            ('39>{Pascha}', 2012, [(24, 5, 2012)]),
            ('39>{Pascha}', 2013, [(13, 6, 2013)]),
            ('39>{Pascha}', 2014, [(29, 5, 2014)]),
            ('39>{Pascha}', 2015, [(21, 5, 2015)]),
            # День святой троицы
            ('49>{Pascha}', 2010, [(23, 5, 2010)]),
            ('49>{Pascha}', 2011, [(12, 6, 2011)]),
            ('49>{Pascha}', 2012, [(3, 6, 2012)]),
            ('49>{Pascha}', 2013, [(23, 6, 2013)]),
            ('49>{Pascha}', 2014, [(8, 6, 2014)]),
            ('49>{Pascha}', 2015, [(31, 5, 2015)]),
            #Преображение Господне
            ('19.08', 2010, [(19, 8, 2010)]),
            ('19.08', 2011, [(19, 8, 2011)]),
            #Успение Пресвятой Богородицы
            ('28.08', 2010, [(28, 8, 2010)]),
            ('28.08', 2011, [(28, 8, 2011)]),
            #Покров Пресвятой Богородицы
            ('14.10', 2010, [(14, 10, 2010)]),
            ('14.10', 2011, [(14, 10, 2011)]),
            # Обрезание Господне
            ('14.01', 2010, [(14, 1, 2010)]),
            ('14.01', 2011, [(14, 1, 2011)]),
            #Рождество Иоанна Предтечи
            ('07.07', 2010, [(7, 7, 2010)]),
            ('07.07', 2011, [(7, 7, 2011)]),
            #День апостолов петра и павла
            ('12.07', 2010, [(12, 7, 2010)]),
            ('12.07', 2011, [(12, 7, 2011)]),
            #Усекновение главы иона Предтечи
            ('11.09', 2010, [(11, 9, 2010)]),
            #Усекновение главы иона Предтечи
            ('11.09', 2011, [(11, 9, 2011)]),
            #Рождественский сочельник
            ('06.01', 2011, [(6, 1, 2011)]),
            #Богоявленский сочельник
            ('18.01', 2011, [(18, 1, 2011)]),
            #  дни особого поминовения усопших
            #   Мясопустная вселенская родительская суббота
            ('57<{Pascha}', 2010, [(6, 2, 2010)]),
            ('57<{Pascha}', 2011, [(26, 2, 2011)]),
            ('57<{Pascha}', 2012, [(18, 2, 2012)]),
            #Родительская вселенская суббота
            (
                '36<{Pascha},29<{Pascha},22<{Pascha}', 2010,
                [(27, 2, 2010), (06, 3, 2010), (13, 3, 2010)]
            ),
            (
                '36<{Pascha},29<{Pascha},22<{Pascha}', 2011,
                [(19, 3, 2011), (26, 3, 2011), (02, 4, 2011)]
            ),
            (
                '36<{Pascha},29<{Pascha},22<{Pascha}', 2012,
                [(10, 3, 2012), (17, 3, 2012), (24, 3, 2012)]
            ),
            #Радоница
            ('9>{Pascha}', 2010, [(13, 4, 2010)]),
            ('9>{Pascha}', 2011, [(3, 5, 2011)]),
            ('9>{Pascha}', 2012, [(24, 4, 2012)]),
            #   9-го мая
            ('09.05', 2010, [(9, 5, 2010)]),
            #Троицкая вселенская родительская суббота
            ('48>{Pascha}', 2010, [(22, 5, 2010)]),
            ('48>{Pascha}', 2011, [(11, 6, 2011)]),
            ('48>{Pascha}', 2012, [(2, 6, 2012)]),
            #Димитриевская суббота
            ('02.11~08.11|0000010', 2010, [(6, 11, 2010)]),
            ('02.11~08.11|0000010', 2011, [(5, 11, 2011)]),
            ('02.11~08.11|0000010', 2012, [(3, 11, 2012)]),
            #  дни четырдесятницы
            #  Неделя мытаря и фарисея
            ('70<{Pascha}', 2011, [(13, 2, 2011)]),
            ('70<{Pascha}', 2012, [(5, 2, 2012)]),
            ('70<{Pascha}', 2013, [(24, 2, 2013)]),
            #  Неделя о блудном сыне
            ('63<{Pascha}', 2011, [(20, 2, 2011)]),
            ('63<{Pascha}', 2012, [(12, 2, 2012)]),
            ('63<{Pascha}', 2013, [(3, 3, 2013)]),
            #  Неделя о Страшном суде. Заговенье на мясо
            ('56<{Pascha}', 2011, [(27, 2, 2011)]),
            ('56<{Pascha}', 2012, [(19, 2, 2012)]),
            ('56<{Pascha}', 2013, [(10, 3, 2013)]),
            #  Прощеное воскресенье - Неделя сыропустная
            ('49<{Pascha}', 2011, [(6, 3, 2011)]),
            ('49<{Pascha}', 2012, [(26, 2, 2012)]),
            ('49<{Pascha}', 2013, [(17, 3, 2013)]),
            #  тожество православия
            ('42<{Pascha}', 2011, [(13, 3, 2011)]),
            ('42<{Pascha}', 2012, [(4, 3, 2012)]),
            ('42<{Pascha}', 2013, [(24, 3, 2013)]),
            #Неделя 2-я Великого поста Святителя Григория Паламы
            ('35<{Pascha}', 2011, [(20, 3, 2011)]),
            ('35<{Pascha}', 2012, [(11, 3, 2012)]),
            ('35<{Pascha}', 2013, [(31, 3, 2013)]),
            #Неделя 3-я Великого поста
            ('28<{Pascha}', 2011, [(27, 3, 2011)]),
            ('28<{Pascha}', 2012, [(18, 3, 2012)]),
            ('28<{Pascha}', 2013, [(7, 4, 2013)]),
            #Иоанна Лествичника
            ('21<{Pascha}', 2011, [(3, 4, 2011)]),
            ('21<{Pascha}', 2012, [(25, 3, 2012)]),
            ('21<{Pascha}', 2013, [(14, 4, 2013)]),
            #Марии Египетской
            ('14<{Pascha}', 2011, [(10, 4, 2011)]),
            ('14<{Pascha}', 2012, [(1, 4, 2012)]),
            ('14<{Pascha}', 2013, [(21, 4, 2013)]),
            #Суббота акафиста
            ('15<{Pascha}', 2011, [(9, 4, 2011)]),
            ('15<{Pascha}', 2012, [(31, 3, 2012)]),
            ('15<{Pascha}', 2013, [(20, 4, 2013)]),
            # Марьино стояние
            ('17<{Pascha}', 2011, [(7, 4, 2011)]),
            ('17<{Pascha}', 2012, [(29, 3, 2012)]),
            ('17<{Pascha}', 2013, [(18, 4, 2013)]),
            #  Лазарева суббота
            ('8<{Pascha}', 2011, [(16, 4, 2011)]),
            ('8<{Pascha}', 2012, [(7, 4, 2012)]),
            ('8<{Pascha}', 2013, [(27, 4, 2013)]),
            # последнее воскресенье мая
            ('01.05~31.05|0000001|-1', 2011, [(29, 5, 2011)]),
            ('01.05~31.05|0000001|-1', 2012, [(27, 5, 2012)]),
            #  последнее воскресенье октября
            ('01.10~31.10|0000001|-1', 2011, [(30, 10, 2011)]),
            ('01.10~31.10|0000001|-1', 2012, [(28, 10, 2012)]),
            (
                '[01.05~31.05|0000001|-1]~[01.10~31.10|0000001|-1]', 2011,
                get_period((29, 5, 2011), (30, 10, 2011))
            ),
        )

    @data_provider(provider_function)
    def test_function(self, formula, year, dates_list):
        list_d = smart_function(formula, year)
        self.assertEquals(
            list_d, dates_list,
            'в формуле {0} ошибка. должно {1} получилось {2}'.format(
                formula, dates_list, list_d
            )
        )
