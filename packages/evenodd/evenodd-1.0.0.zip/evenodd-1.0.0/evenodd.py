'''
This module is used for detecting even numbers and odd numbers using the function
called "even_odd" which will tell that whether the number is a even or odd.
'''
def even_odd(num):
    '''
    This function will tell whether the given number is an even or an odd

    >>> even_odd(44)
    Even
    >>> even_odd(47)
    Odd
    '''
    if num % 2 == 0:
        print ("Even")
    elif num % 2 == 0:
        print ("Odd")
        
