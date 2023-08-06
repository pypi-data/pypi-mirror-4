# _*_ coding: utf-8; _*_

import smblink
import unittest

"""
Configure
"""
unittestVerbosity = 0 # unittest.main(verbosity=N) level
verboseMode = False   # print out test case details

"""
Test Case
"""
class TestSequenceFunctions(unittest.TestCase): #unittest.TestCaseのサブクラスとしてテストケース作成

  def setUp(self):
    if verboseMode : print "\n"

  def test_convertToWSLStyle_simpleStr(self):
    chkList = [
        # [ input , output ]
        [r'\\',r'//'],
        [r'\\path',r'//path'],
        [r'\\hoge\new\to\path',r'//hoge/new/to/path'],
        [r'\\hoge\space space\to\path',r'//hoge/space%20space/to/path'],
        [r'\\hoge\^~{}[];@\=&$# \to\path',r'//hoge/%5E%7E%7B%7D%5B%5D%3B%40/%3D%26%24%23%20/to/path'],
        [r'\\hoge\\%=%&$# \to\path',r'//hoge//%25%3D%25%26%24%23%20/to/path'],
      ]
    for chk in chkList:
      self.assertEqual( chk[1], smblink.convertToWSLStyle( chk[0] ) )
      if verboseMode : print " Input  : "+chk[0]+"\n Assert : "+chk[1] + "\n ---- "

  def test_convertToWSLStyle_multibyteStr(self):
    chkList = [
        # [ input , output ]
        [u'\\\\日本語ほげほげ',u'//日本語ほげほげ'],
        [u'\\\\日本語ほげほげ\\日本語ふがふが',u'//日本語ほげほげ/日本語ふがふが'],
        [u'\\\\日本語^~{}[];@ほげほげ\\日本語=&$# ふがふが',u'//日本語%5E%7E%7B%7D%5B%5D%3B%40ほげほげ/日本語%3D%26%24%23%20ふがふが'],
      ]
    for chk in chkList:
      self.assertEqual( chk[1], smblink.convertToWSLStyle( chk[0] ) )
      if verboseMode : print " Input  : "+chk[0]+"\n Assert : "+chk[1] + "\n ---- "

  def test_smblink_role(self):
    chkList = [
        # [ input , output ]
        [r':smblink:`\\path`', r'<a href="file://path">\\path</a>'],
        [u':smblink:`\\\\日本語ほげほげ`',u'<a href="file://日本語ほげほげ">\\\\日本語ほげほげ</a>'],
        [r'`\\path`', r'<a href="file://path">\\path</a>'],
        [r'\\path`', r'<a href="file:"></a>'],
        [r'`\\path', r'<a href="file://path">\\path</a>'],
        [r'\\path', r'<a href="file://path">\\path</a>'],
        [r':smblink: `hoge <\\path>`', r'<a href="file://path">hoge</a>'],
        [r':smblink: `hoge<\\path>`', r'<a href="file://path">hoge</a>'],
        [r':smblink: `hoge        <\\path>    `', r'<a href="file://path">hoge</a>'],
      ]
    for chk in chkList:
      self.assertEqual( chk[1] , 
          smblink.smblink_role("smblink", chk[0], '','','','')[0][0].astext() )
      if verboseMode : print u" Input  : " + chk[0] + u"\n Assert : " + chk[1] + u"\n ---- "

"""
Main
"""
if __name__ == '__main__':
  unittest.main(verbosity=unittestVerbosity)

"""
test_suite
"""
def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TestSequenceFunctions))
  return suite
