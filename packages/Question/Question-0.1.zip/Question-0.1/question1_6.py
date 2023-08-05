"""question description:
     Given an image represented by an NxN matrix, where each pixel in the image
     is 4 bytes, write a method to rotate the image by 90 degrees. Can you do
     this in place?
     
"""
def solution1(array):
    """   
    first we swap the matrix. Then do a X axis mirror
    (i,j) ->(j,i) ->(j,N-1-i)
    (j,N-1-i) ->(N-1-i,j)->(N-1-i,N-1-j)
    (N-1-i,N-1-j) ->(N-1-j,N-1-i) ->(N-1-j,i)
    (N-1-j,i)->(i,N-1-j)->(i,j)
    So we should change the value of matrix:
        (i,j)->(j,N-1-i)->(N-1-i,N-1-j)->(N-1-j,i)->(i,j)
        
    >>> a = [[1,2,3],[4,5,6],[7,8,9]]
    >>> solution1(a)
    [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
    """ 
    N = len(array)
    for i in range(0,N/2):
        for j in range(i,(N+1)/2):
            #print "(%s,%s)->(%s,%s)->(%s,%s)->(%s,%s)" % (i,j,j,N-1-i,N-1-i,N-1-j,N-1-j,i)
            temp = array[i][j]
            array[i][j] = array[N-1-j][i]
            array[N-1-j][i] = array[N-1-i][N-1-j]
            array[N-1-i][N-1-j] = array[j][N-1-i]
            array[j][N-1-i] = temp
    
    return array           

    
            
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
    """User can also run test on commmand line.
    python -m doctest -v [filename].py
    
    Further reading:
        (1) built-in data type str
        (2) Learn the itertool of Python       
    """