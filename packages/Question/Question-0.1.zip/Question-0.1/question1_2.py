"""question description:
        Write code to reverse a C-Style String. (C-String means that "abcd" 
        is represented as five characters, including the null character.)        
"""

def solution1(word):
    """
    First please notice there is no C-Style string in python. You can add
    \0 NULL charcter at the end to simuate it.
    Second, string in python is immutable.So you can not change a string 's 
    value. But you can use a new string.
    
    >>> solution1("abcd\\0")
    'dcba'
    >>> solution1("tree\\0")
    'eert'
    """
    answer = word[:-1] #remove this last NULL charachter
    answer = answer[::-1] #reverse the string
    return answer    


    
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    """