"""question description:
      Write a method to decide if two strings are anagrams or not.  
      (anagrams mean two string use same charcthters with differnt order.
      For example, "Dave Barry" = "Ray Adverb"
      "Tom Cruise" = "So I'm cuter")
"""

def solution1(word1,word2):
    """
    use dict
    
    >>> solution1("Dave Barry","Ray Adverb")
    True
    >>> solution1("Dave Barr","Ray Adverb")
    False
    >>> solution1("Tom Cruise","SoIm cuter")
    True
    """
    input1 = word1.lower()
    input2 = word2.lower()
    myset = set(input1).union(set(input2))
    
    for c in myset:
        if(input1.count(c) != input2.count(c)):
            return False                
    return True         
    
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    
    Further reading:
        (1) built-in data type str
        (2) Learn the itertool of Python       
    """