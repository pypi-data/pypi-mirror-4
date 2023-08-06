""" Utility functions."""
# Author  : Sourabh Bajaj
# Date    : 26th April, 2013
# Email   : sourabhbajaj@gatech.edu
# Summary : Testing Utils file
# License : BSD License

def print_string():
    """This function prints a string.
    
    :returns: None.
    :output: print an string.
    :rtype: None.
    """
    print "This is a sample string."
    print "Author : Sourabh Bajaj"
    return


def print_integer(i=100):
    """This function prints the integer i.
    
    :param i: The integer to be printed.
    :returns: None.
    :rtype: None.
    :output: print an integer
    """
    print "This is a sample integer.", i
    return

def main():
    '''
    This is the main function
    '''
    print "This is the main function"


if __name__ == '__main__':
    main()
