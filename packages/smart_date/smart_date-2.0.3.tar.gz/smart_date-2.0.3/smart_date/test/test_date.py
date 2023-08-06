# -*- coding: utf-8 -*-
# pylint: disable=C0302, E0211, R0201
import datetime
from unittest import TestCase
from smart_date import date
from smart_date.test.data_provider import data_provider

class DateTest(TestCase):
    def provider_is_leap_year():
        return (
            (1700, False),
            (1800, False),
            (1900, False),
            (1600, True),
            (2000, True),
            (2100, False),
            (2200, False),
            (2300, False)
        )

    '''
    тестируем фунции вечного времени
    '''
    @data_provider(provider_is_leap_year)
    def test_is_leap_year(self, year, result):
        if result:
            self.assertTrue(
                date.is_leap_year(year),
                '{0} должен быть високосным'.format(year)
            )
        else:
            self.assertFalse(
                date.is_leap_year(year),
                '{0} должен не быть високосным'.format(year)
            )

    def provider_date_compare():
        return (
            ('3.11.1983', '3.10.1983', -1),
            ('3.11.1183', '2.11.1183', -1),
            ('3.11.1183', '3.11.1182', -1),
            ('3.11.1183', '4.11.1183', 1),
            ('3.11.1183', '3.12.1183', 1),
            ('3.11.1183', '3.11.1184', 1),
            ('3.11.1983', '2.01.1984', 1),
            ('3.11.1983', '3.11.1983', 0),

        )

    @data_provider(provider_date_compare)
    def test_date_compare(self, year1, year2, result):
        '''
        тестируем сравнение дат
        '''
        self.assertEquals(
            date.date_compare(*year1.split('.') + year2.split('.')),
            result,
            '{0} and {1} result {2}'.format(year1, year2, result)
        )

    def provider_num_days_in_month():
        return (
            ('1.1911', 31),
            ('2.1911', 28),
            ('2.2000', 29),
            ('3.1911', 31),
            ('4.1911', 30),
            ('5.1911', 31),
            ('6.1911', 30),
            ('7.1911', 31),
            ('8.1911', 31),
            ('9.1911', 30),
            ('10.1911', 31),
            ('11.1911', 30),
            ('12.1911', 31),
            ('2.2012', 29),
        )

    @data_provider(provider_num_days_in_month)
    def test_num_days_in_month(self, month_year, days):
        '''
        тестируем вычисление количества дней в месяце
        '''
        result = date.num_days_in_month(*month_year.split('.'))
        self.assertEquals(
            result, days,
            '{0} должно быть {1} дней, а получилось {2}'.format(
                month_year, days, result
            )
        )

    def provider_date_shift():
        return (
            ('1.1.1983', 10, '11.1.1983'),
            ('24.1.1983', 17, '10.2.1983'),
            ('24.1.1983', -4, '20.1.1983'),
            ('20.2.2000', 20, '11.3.2000'),
            ('20.2.2001', 20, '12.3.2001'),
            ('20.2.2001', 50, '11.4.2001'),
            ('23.12.1983', 10, '2.1.1984'),
            ('15.4.2012', -48, '27.2.2012'),
        )

    @data_provider(provider_date_shift)
    def test_date_shift(self, date_before, delta, date_after):
        '''
        тестируем смещение даты
        '''
        date_shift = date.date_shift(*date_before.split('.') + [delta])
        date_shift_str = '.'.join(map(str, date_shift))
        message = "после смещения даты {0} на {1} дней, " +\
                  "должно получится {2}, a получилось {3}".\
                  format(date_before, delta, date_after, date_shift_str)
        self.assertEquals(date_shift_str, date_after, message)

    def provider_get_day_of_week():
        return (
            ('31.12.2008', 3),
            ('17.11.2012', 6),
            ('30.07.2012', 1),
            ('12.01.2012', 4),
        )

    @data_provider(provider_get_day_of_week)
    def test_get_day_of_week(self, test_date, week_day):
        '''
        тестируем определения дня недели
        '''
        result = date.get_day_of_week(*test_date.split('.'))
        message = '{0} должен приходится на {1} день недели' \
                  ' а получился на {2}'.format(test_date, week_day, result)
        self.assertEquals(result, week_day, message)

    def provider_is_date_correct():
        return (
            ('3.11.1983', True),
            ('29.02.2000', True),
            ('29.02.2001', False),
            ('31.04.2001', False),
            ('32.05.2001', False),
            ('11.15.2001', False),
        )

    @data_provider(provider_is_date_correct)
    def test_is_date_correct(self, day, is_corrcet):
        '''
        тестируем проверку даты на корретность
        '''
        if is_corrcet:
            self.assertTrue(
                date.is_date_correct(*day.split('.')),
                '{0} должна быть корректной'.format(day)
            )
        else:
            self.assertFalse(
                date.is_date_correct(*day.split('.')),
                '{0} должна быть некорректной'.format(day)
            )

    def provider_pascha():
        return (
            (1918, '5.5.1918'),
            (1919, '20.4.1919'),
            (1920, '11.4.1920'),
            (1932, '1.5.1932'),
            (1933, '16.4.1933'),
            (2017, '16.4.2017'),
            (2024, '5.5.2024'),
            (2036, '20.4.2036'),
            (2049, '25.4.2049'),


        )

    @data_provider(provider_pascha)
    def test_pascha(self, year, day):
        '''
        тестируем вычисление даты православной пасхи
        '''
        result = '.'.join(map(str, date.Pascha(year)))
        message = 'в {0} году пасха должна приходится на {1}'\
                  ' а получается на {2}'.format(year, day, result)
        self.assertEquals(result, day, message)

    def test_get_current_year(self):
        '''
        говно тест
        '''
        dt_now = datetime.datetime.now()
        year = int(dt_now.strftime('%Y'))
        self.assertEquals(year, date.get_current_year())
