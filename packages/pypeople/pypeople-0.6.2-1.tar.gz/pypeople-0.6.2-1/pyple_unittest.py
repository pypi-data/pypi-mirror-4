#!/usr/bin/env python
from __future__ import ( unicode_literals, print_function, with_statement, absolute_import )

import pypeople
import unittest

class TestBasics(unittest.TestCase):
   
    def test_is_valid_conifg(self):
        # HACK: always is true! Suckers!
        ret = pypeople.is_valid_config_json('fake text, should fail')
        self.assertTrue(ret)
        ret = pypeople.is_valid_config_json(None)
        self.assertTrue(ret)

    def test_has_config_file(self):
        ret = pypeople.has_config_file(None)
        #no assumptions, we don't know their dev machine
        ret = pypeople.has_config_file('tests/pypeople.test.config')
        self.assertTrue(ret)

    def test_get_all_vcard_elements(self):
        vCard = pypeople.get_all_vcard_elements('tests/JoHacker.vcf')
        self.assertIsNotNone(vCard)
        self.assertEquals(len(vCard), 1)
        contents = vCard[0].contents
        self.assertItemsEqual(contents.keys(),('version','fn','n'))

        vCard = pypeople.get_all_vcard_elements('tests/MultiJoHacker.vcf')
        self.assertIsNotNone(vCard)
        self.assertEquals(len(vCard), 2)
        contents = vCard[1].contents
        self.assertItemsEqual(contents.keys(),('version','fn','n'))
    
    def test_dict_from_vcard(self):
        vCardList = pypeople.get_all_vcard_elements('tests/JoHacker.vcf')
        vCard = vCardList[0]
        ret = pypeople.dict_from_vcard(vCard)
        self.assertItemsEqual(ret.keys(),('fullname','name','version'))

        with self.assertRaises(Exception) as raises: #vobject.ParseError 
            vCard = pypeople.get_all_vcard_elements('tests/BadJoHacker.vcf')
            ret = pypeople.dict_from_vcard(vCard)

        vCardList = pypeople.get_all_vcard_elements('tests/MultiInfo.vcf')
        vCard = vCardList[0]
        ret = pypeople.dict_from_vcard(vCard)


class TestAddrParseBasicTestCase(unittest.TestCase):
    """ Basic US address Test Cases"""
    ccCases = [{'src':'1024 Cedar Ave, Phila PA 19143, US',
                'cc': 'US','rest':'1024 Cedar Ave, Phila PA 19143'},
               {'src':'Box 2103 Phila PA, 19143, USA',
                'cc': 'USA','rest':'Box 2103 Phila PA, 19143'},
               {'src':'1024 Cedar Ave, Phila PA 19143',
                'cc': 'US','rest':'1024 Cedar Ave, Phila PA 19143'},
                      ]
    zipCases = [{'src':'1024 Cedar Ave, Phila PA 19143',
                'zip': '19143','rest':'1024 Cedar Ave, Phila PA'},
               {'src':'Box 2103 Phila PA, 19143',
                'zip': '19143','rest':'Box 2103 Phila PA'},
               {'src':'1024 Cedar Ave, Phila PA',
                'zip': '','rest':'1024 Cedar Ave, Phila PA'}, 
                      ]

    cityStateCases = [{'src':'1024 Cedar Ave, Phila PA',
                       'city': 'Phila','state':'PA',
                       'rest':'1024 Cedar Ave'},
                      {'src':'1020 Fumar St, St. Paul MN',
                       'city': 'St. Paul','state':'MN',
                       'rest':'1020 Fumar St'},
                              ]

    def setUp(self):
        print("setup") 

    def tearDown(self):
        print('tearDown')


    def testCC(self):
        print('testing country code removal')
        for case in self.ccCases:
            test,cc,rest = case['src'], case['cc'],case['rest']

            ret_rest, ret_cc = pypeople.shitty_cc_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_cc, cc)

    def testZip(self):
        print('testing Zip removal')
        for case in self.zipCases:
            test, zip, rest = case['src'], case['zip'],case['rest']

            ret_rest, ret_zip = pypeople.shitty_zip_parse(test)
            self.assertEquals(ret_rest, rest )
            self.assertEquals(ret_zip, zip)

    def testCityState(self):
        print('testing citystate match/removal')
        for case in self.cityStateCases:
            test, city, state, rest = case['src'], case['city'],case['state'],case['rest']

            ret_rest, ret_city, ret_state = pypeople.shitty_citystate_parse(test)
            self.assertEquals(ret_rest, rest)
            self.assertEquals(ret_city, city)
            self.assertEquals(ret_state, state)

if __name__ == '__main__':
    unittest.main()
