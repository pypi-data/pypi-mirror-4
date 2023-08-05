"""question description:
        Implement an algorithm to determine if a string has all unique
        characters.What if you can not use additional data structures?
    solution:
        1st step we should define the function interface, input is a string,
        the output is a boolean True or False. If a string has all unique 
        characters,return True.
        2nd step you can ask the interviewer give some example to clarify, you 
        you can give some example to clarify. For example, 
        (1) string "Hello" should return False
        (2) string "university" should return False, but "univer" should return
        True.
        3rd step, from example,we can see clearly if only 1 charcter appear only
        1 times, it should return True. If it appears more than 1 times, return
        False.
        4th step, tell the inteviewer, we can ignore the asumpption (do not use
        additional data structures) first, and solve this problem use the 
        straighforward view. See solution1.
        
        
"""

def solution1(word):
    """
    use additional data structure dict
    
    >>> solution1('Hello')
    False
    >>> solution1('Helo')
    True
    """
    a = dict()
    for c in word:
        if(a.has_key(c)):
            a[c]+=1
            return False
        else:
            a[c] = 1
    
    return True
    

def solution2(word):
    """
    Do not use additional data strcture
    For simplicity, assume char set is ASCII 
    (if not, we need to increase the storage size. The rest of the logic would
    be the same). NOTE: This is a great thing to point out to your interviewer!
    
    >>> solution2('Hello')
    False
    >>> solution2('Helo')
    True
    """
    checker = 0
    length = len(word)
    for i in range(0,length):
        val = ord(word[i])        
        if((checker & (1<<val)) >0):
            return False
        checker |=(1<<val)
    return True
    
def solution3(word):
    """
    Use addtional data strcture set
    
    >>> solution3('Hello')
    False
    >>> solution3('Helo')
    True
    """
    myset = set()
    length = len(word)
    
    for c in word:
        myset.add(c)
    
    if len(myset) == length:
        return True
    else:
        return False
def solution4(mystr):
    """
    >>> solution4("Hello")
    False
    >>> solution4("Helo")
    True
    >>> solution4("university")
    False
    """
    
    for c in mystr:
        n = mystr.count(c)
        if n > 1:
            return False    
    return True
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    """

"""Further reading:
    (1) About what is ASCII on wikipedia.
    (2) Learn how to use bitwise operator on python.
        http://wiki.python.org/moin/BitwiseOperators
    (3) Learn built-in function ord
"""
    




