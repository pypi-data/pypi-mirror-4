""" File to test the utility functions."""
# Author  : Sourabh Bajaj
# Date    : 26th April, 2013
# Email   : sourabhbajaj@gatech.edu
# Summary : Testing Utils file
# License : BSD License

# Python imports
import unittest

#DemoPackage imports
import DemoPackage.utils


class TestUtils(unittest.TestCase):
    """Unittest Class
    """

    def setUp(self):
        """ Unittest setup function and declares a Sequence of 10 numbers.
        
        :param self: 
        :returns: None
        """
        self.seq = range(10)

    def test_print_integer(self):
        """Testing the print_integer function.
        
        :param self:
        :returns: None
        """
        print "Sequence : ", self.seq
        DemoPackage.utils.print_integer()

    def test_print_string(self):
        """Testing the print_string function.
        
        :param self:
        :returns: None
        """
        print "Sequence : ", self.seq
        DemoPackage.utils.print_string()


if __name__ == '__main__':
    unittest.main()
