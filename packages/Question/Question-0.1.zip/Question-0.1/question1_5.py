"""question description:
     Write a method to replace all spaces in a string with %20
"""
def solution1(word):
    """
    >>> solution1(" ")
    '%20'
    """ 
    temp = word
    temp = temp.replace(" ",'%20')
    return temp
    
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    
    Further reading:
        (1) built-in data type str
        (2) Learn the itertool of Python       
    """