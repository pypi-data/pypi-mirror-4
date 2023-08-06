#!/usr/bin/env python

import unittest
import valid_edtf
from dateutil import rrule
from datetime import datetime, timedelta


class isValidBadInput(unittest.TestCase):

    def testIntervalMalformed(self):

        # is_valid_interval should fail if not 8601 extended interval
        self.assertFalse(valid_edtf.is_valid_interval('2012/2011'))

    def testEDTFDateTime(self):

        # is_valid should fail if match doesn't exist
        self.assertFalse(valid_edtf.is_valid("2012-10-10T10:10:1"))
        self.assertFalse(valid_edtf.is_valid("2012-10-10T1:10:10"))
        self.assertFalse(valid_edtf.is_valid("2012-10-10T10:1:10"))
        self.assertFalse(valid_edtf.is_valid("2012-10-10t10:10:10"))
        self.assertFalse(valid_edtf.is_valid("2012-10-10T10:10:10Z10"))
        self.assertTrue(valid_edtf.is_valid("2012-10-10T10:10:10Z"))

    def testEDTFInterval(self):

        self.assertTrue(valid_edtf.is_valid("-1000/-0999"))
        self.assertTrue(valid_edtf.is_valid("-1000/-0090-10"))
        self.assertTrue(valid_edtf.is_valid("-1000/2000"))
        self.assertTrue(valid_edtf.is_valid("1000/2000"))
        self.assertTrue(valid_edtf.is_valid("unknown/2000"))
        self.assertTrue(valid_edtf.is_valid("unknown/open"))
        self.assertTrue(valid_edtf.is_valid("0000/0000"))
        self.assertTrue(valid_edtf.is_valid("0000-02/1111"))
        self.assertTrue(valid_edtf.is_valid("0000-01/0000-01-03"))
        self.assertTrue(valid_edtf.is_valid("0000-01-13/0000-01-23"))
        self.assertTrue(valid_edtf.is_valid("1111-01-01/1111"))
        self.assertTrue(valid_edtf.is_valid("0000-01/0000"))

        self.assertFalse(valid_edtf.is_valid("2012/2013/1234/55BULBASAUR"))
        self.assertFalse(valid_edtf.is_valid("NONE/unknown"))
        self.assertFalse(valid_edtf.is_valid("2012///4444"))
        self.assertFalse(valid_edtf.is_valid("2012\\2013"))
        self.assertFalse(valid_edtf.is_valid("2000/12-12"))
        self.assertTrue(valid_edtf.is_valid("2000-uu/2012"))
        self.assertTrue(valid_edtf.is_valid("2000-12-uu/2012"))
        self.assertTrue(valid_edtf.is_valid("2000-uu-10/2012"))
        self.assertTrue(valid_edtf.is_valid("2000-uu-uu/2012"))
        self.assertTrue(valid_edtf.is_valid("2000/2000-uu-uu"))
        self.assertFalse(valid_edtf.is_valid("0800/-0999"))
        self.assertFalse(valid_edtf.is_valid("-1000/-2000"))
        self.assertFalse(valid_edtf.is_valid("1000/-2000"))
        self.assertFalse(valid_edtf.is_valid("y-61000/-2000"))
        self.assertFalse(valid_edtf.is_valid("0001/0000"))
        self.assertFalse(valid_edtf.is_valid("0000-01-03/0000-01"))
        self.assertFalse(valid_edtf.is_valid("0000/-0001"))
        self.assertFalse(valid_edtf.is_valid("0000-02/0000"))

    def testLevel0(self):

        self.assertTrue(valid_edtf.isLevel0('2001-02-03'))
        self.assertTrue(valid_edtf.isLevel0('2008-12'))
        self.assertTrue(valid_edtf.isLevel0('2008'))
        self.assertTrue(valid_edtf.isLevel0('-0999'))
        self.assertTrue(valid_edtf.isLevel0('-9999'))
        self.assertTrue(valid_edtf.isLevel0('0000'))
        self.assertTrue(valid_edtf.isLevel0('2001-02-03T09:30:01'))
        self.assertTrue(valid_edtf.isLevel0('2004-01-01T10:10:10Z'))
        self.assertTrue(valid_edtf.isLevel0('2012-10-10T10:10:10Z'))
        self.assertTrue(valid_edtf.isLevel0('2004-01-01T10:10:10+05:00'))
        self.assertTrue(valid_edtf.isLevel0('1964/2008'))
        self.assertTrue(valid_edtf.isLevel0('2004-06/2006-08'))
        self.assertTrue(valid_edtf.isLevel0('2004-02-01/2005-02-08'))
        self.assertTrue(valid_edtf.isLevel0('2004-02-01/2005-02'))
        self.assertTrue(valid_edtf.isLevel0('2004-02-01/2005'))
        self.assertTrue(valid_edtf.isLevel0('2005/2006-02'))

    def testLevel1(self):

        self.assertTrue(valid_edtf.isLevel1('1984?'))
        self.assertTrue(valid_edtf.isLevel1('2004-06?'))
        self.assertTrue(valid_edtf.isLevel1('2004-06-11?'))
        self.assertTrue(valid_edtf.isLevel1('1984~'))
        self.assertTrue(valid_edtf.isLevel1('1984?~'))
        self.assertTrue(valid_edtf.isLevel1('199u'))
        self.assertTrue(valid_edtf.isLevel1('19uu'))
        self.assertTrue(valid_edtf.isLevel1('1999-uu'))
        self.assertTrue(valid_edtf.isLevel1('1999-01-uu'))
        self.assertTrue(valid_edtf.isLevel1('1999-uu-uu'))
        self.assertTrue(valid_edtf.isLevel1('unknown/2006'))
        self.assertTrue(valid_edtf.isLevel1('2004-06-01/unknown'))
        self.assertTrue(valid_edtf.isLevel1('2004-01-01/open'))
        self.assertTrue(valid_edtf.isLevel1('1984~/2004-06'))
        self.assertTrue(valid_edtf.isLevel1('1984/2004-06~'))
        self.assertTrue(valid_edtf.isLevel1('1984~/2004~'))
        self.assertTrue(valid_edtf.isLevel1('1984?/2004?~'))
        self.assertTrue(valid_edtf.isLevel1('1984-06?/2004-08?'))
        self.assertTrue(valid_edtf.isLevel1('1984-06-02?/2004-08-08~'))
        self.assertTrue(valid_edtf.isLevel1('1984-06-02?/unknown'))
        self.assertTrue(valid_edtf.isLevel1('y170000002'))
        self.assertTrue(valid_edtf.isLevel1('y-170000002'))
        self.assertTrue(valid_edtf.isLevel1('2001-21'))
        self.assertTrue(valid_edtf.isLevel1('2003-22'))
        self.assertTrue(valid_edtf.isLevel1('2000-23'))
        self.assertTrue(valid_edtf.isLevel1('2010-24'))

    def testLevel2(self):

        self.assertTrue(valid_edtf.isLevel2('2004?-06-11'))
        self.assertTrue(valid_edtf.isLevel2('2004-06~-11'))
        self.assertTrue(valid_edtf.isLevel2('2004-(06)?-11'))
        self.assertTrue(valid_edtf.isLevel2('2004-06-(11)~'))
        self.assertTrue(valid_edtf.isLevel2('2004-(06)?~'))
        self.assertTrue(valid_edtf.isLevel2('2004-(06-11)?'))
        self.assertTrue(valid_edtf.isLevel2('2004?-06-(11)~'))
        self.assertTrue(valid_edtf.isLevel2('(2004-(06)~)?'))
        self.assertTrue(valid_edtf.isLevel2('2004?-(06)?~'))
        self.assertTrue(valid_edtf.isLevel2('(2004)?-06-04~'))
        self.assertTrue(valid_edtf.isLevel2('(2011)-06-04~'))
        self.assertTrue(valid_edtf.isLevel2('2011-(06-04)~'))
        self.assertTrue(valid_edtf.isLevel2('2011-23~'))
        self.assertTrue(valid_edtf.isLevel2('156u-12-25'))
        self.assertTrue(valid_edtf.isLevel2('15uu-12-25'))
        self.assertTrue(valid_edtf.isLevel2('15uu-12-uu'))
        self.assertTrue(valid_edtf.isLevel2('1560-uu-25'))
        self.assertTrue(valid_edtf.isLevel2('[1667,1668, 1670..1672]'))
        self.assertTrue(valid_edtf.isLevel2('[..1760-12-03]'))
        self.assertTrue(valid_edtf.isLevel2('[1760-12..]'))
        self.assertTrue(valid_edtf.isLevel2('[1760-01, 1760-02, 1760-12..]'))
        self.assertTrue(valid_edtf.isLevel2('[1667, 1760-12]'))
        self.assertTrue(valid_edtf.isLevel2('{1667,1668, 1670..1672}'))
        self.assertTrue(valid_edtf.isLevel2('{1960, 1961-12}'))
        self.assertTrue(valid_edtf.isLevel2('196x'))
        self.assertTrue(valid_edtf.isLevel2('19xx'))
        self.assertTrue(valid_edtf.isLevel2('2004-06-(01)~/2004-06-(20)~'))
        self.assertTrue(valid_edtf.isLevel2('2004-06-uu/2004-07-03'))
        self.assertTrue(valid_edtf.isLevel2('y17e7'))
        self.assertTrue(valid_edtf.isLevel2('y-17e7'))
        self.assertTrue(valid_edtf.isLevel2('y17101e4p3'))
        self.assertTrue(valid_edtf.isLevel2('2001-21^southernHemisphere'))

    def testEDTFDateMatch(self):

        # is_valid should fail if match doesn't exist
        self.assertFalse(valid_edtf.is_valid("+20067890?~"))
        self.assertFalse(valid_edtf.is_valid("y2006"))
        self.assertFalse(valid_edtf.is_valid("-0000"))
        self.assertFalse(valid_edtf.is_valid("+y20067890-14-10?~"))
        self.assertFalse(valid_edtf.is_valid("+20067890?~"))
        self.assertFalse(valid_edtf.is_valid("+2006?~"))

    def testLength(self):

        # is_valid_length should fail if length not in valid_lengths
        self.assertFalse(valid_edtf.is_valid_length("123"))


if __name__ == "__main__":
    unittest.main()
    print 'done'
