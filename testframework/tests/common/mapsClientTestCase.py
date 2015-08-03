import unittest

from util import TestConfig

class MapsClientTestCase(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    config = MapsEditorConfig()

  @classmethod
  def tearDownClass(cls):
    pass

  def test_upper(self):
      self.assertEqual('foo'.upper(), 'FOO')

  def test_isupper(self):
      self.assertTrue('FOO'.isupper())
      self.assertFalse('Foo'.isupper())

def main():
  unittest.main()

if __name__ == '__main__':
  main()