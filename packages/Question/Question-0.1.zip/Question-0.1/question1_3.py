"""question description:
        Design an algorithm and write code to remove the duplicate characters
        in a string without using any additional buffer. NOTE: One or two
        additional variables are fine. An extra copy of the array is not.
        FOLLOW UP
        Write the test cases for this method.        
"""

def solution1(word):
    """
    First, let us solve this problem without consider the constraint:use buffer
    We can use a dict to keep the info of the charachter. Use a list contain 
    the string.
    
    >>> solution1("tree")
    'tre'
    >>> solution1('aabbccddee')
    'abcde'
    
    """
    temp = dict()
    answer = []
    for c in word:
        if temp.has_key(c):
            continue
        else:
            temp[c] = 1
            answer.append(c)
    
    return ''.join(answer)
    
def solution2(word):
    """
    >>> solution2("tree")
    'tre'
    >>> solution2('aabbccddee')
    'abcde'
    """
    answer = ''
    tag = True
    for oc in word:
        tag = True
        for c in answer:
            if oc == c:
                tag = False
                break       
        if tag:
            answer = ''.join([answer,oc])    
    return answer
        
    
    
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    
    Further reading:
        (1) built-in data type str
        (2) Learn the itertool of Python       
    """