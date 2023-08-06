import numpy as np
import os
import sys
import traceback
import pyneb as pn

def execution_path(filename):
    return os.path.join(os.path.dirname(sys._getframe(1).f_code.co_filename), filename)

def int_to_roman(input_):
    """
    Convert an integer to Roman numerals.
    
    Examples:
    >>> int_to_roman(0)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(-1)
    Traceback (most recent call last):
    ValueError: Argument must be between 1 and 3999
    
    >>> int_to_roman(1.5)
    Traceback (most recent call last):
    TypeError: expected integer, got <type 'float'>
    
    >>> print int_to_roman(2000)
    MM

    >>> print int_to_roman(1999)
    MCMXCIX

    """
    if type(input_) != type(1):
        #raise TypeError, "expected integer, got %s" % type(input_)
        return None
    if not 0 < input_ < 4000:
        #raise ValueError, "Argument must be between 1 and 3999"
        return None
    ints = (1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1)
    nums = ('M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I')
    result = ""
    for i in range(len(ints)):
        count = int(input_ / ints[i])
        result += nums[i] * count
        input_ -= ints[i] * count
    return result

def roman_to_int(input_):
    """
    Convert a roman numeral to an integer.
    
    >>> r = range(1, 4000)
    >>> nums = [int_to_roman(i) for i in r]
    >>> ints = [roman_to_int(n) for n in nums]
    >>> print r == ints
    1
    
    >>> roman_to_int('VVVIV')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: VVVIV

    >>> roman_to_int(1)
    Traceback (most recent call last):
     ...
    TypeError: expected string, got <type 'int'>

    >>> roman_to_int('a')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: A

    >>> roman_to_int('IL')
    Traceback (most recent call last):
     ...
    ValueError: input is not a valid roman numeral: IL

    """   
    if type(input_) != type(""):
        #raise TypeError, "expected string, got %s" % type(input_)
        return None
    input_ = input_.upper()
    nums = ['M', 'D', 'C', 'L', 'X', 'V', 'I']
    ints = [1000, 500, 100, 50, 10, 5, 1]
    places = []
    for c in input_:
        if not c in nums:
            #raise ValueError, "input is not a valid roman numeral: %s" % input_
            return None
    for i in range(len(input_)):
        c = input_[i]
        value = ints[nums.index(c)]
        # If the next place holds a larger number, this value is negative.
        try:
            nextvalue = ints[nums.index(input_[i + 1])]
            if nextvalue > value:
                value *= -1
        except IndexError:
            # there is no next place.
            pass
        places.append(value)
    sum_ = 0
    for n in places: sum_ += n
    # Easiest test for validity...
    if int_to_roman(sum_) == input_:
        return sum_
    else:
        #raise ValueError, 'input is not a valid roman numeral: %s' % input_
        return None
      
def parseAtom(atom):
    '''Parses an atom label into the element and spectrum parts'''

    elem = ''
    spec = ''
    for l in atom:
        if l.isdigit():
            spec = spec + l
        if l.isalpha():
            elem = elem + l
    return elem, spec

def strExtract(text, par1=None, par2=None): 
    """
    Extract a substring from text (first parameter)
     
    If par1 is a string, the extraction starts after par1,
    else if it is an integer, it starts at position par1.
    If par 2 is a string, extraction stops at par2, 
    else if par2 is an integer, extraction stops after par2 characters.
    
    Examples: 
    
    strExtract('test123','e','1')
    strExtract('test123','st',4)
    
    """
    if np.size(text) == 1:
        if type(par1) is int:
            str1 = text[par1::]
        elif type(par1) is str:
            str1 = text.split(par1)[-1]
        else:
            str1 = text
    
        if type(par2) is int:
            str2 = str1[0:par2]
        elif type(par2) is str:
            str2 = str1.split(par2)[0]
        else:
            str2 = str1
        return str2
    else:
        res = []
        for subtext in text:
            res1 = strExtract(subtext, par1=par1, par2=par2)
            if res1 != '':
                res.append(res1)
        return res

def formatExceptionInfo(maxTBlevel=5):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    return (excName, excArgs, excTb)

def multi_split(s, seps):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res


def cleanPypicFiles(files=None, all_=False, dir_=None):
    """
    Method to clean the directory containing the pypics files.
    Parameters:
        - files : list of files to be removed
        - all_ :    Boolean, is set to True, all the files are deleted from the directory
        - dir_ :    directory from where the files are removed. 
                If None (default), pn.pypic_path is used.
    """
    if dir_ is None:
        dir_ = pn.config.pypic_path
    if all_:
        files = os.listdir(dir_)
        if np.ndim(files) == 0:
            files = [files]
    if files is None:
        return
    for file_ in files:
        file_path = os.path.join(dir_, file_)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                pn.log_.message('Deleting {0}'.format(file_path), calling = 'cleanPypicFiles')
        except:
            pn.log_.warn('Unable to remove {0}'.format(file_path), calling = 'cleanPypicFiles')

def getPypicFiles(dir_=None):
    """
    Return the list of files in the directory.
    Parameters:
        - dir_ :    directory from where the files are removed. 
                If None (default), pn.pypic_path is used.
    """
    if dir_ is None:
        dir_ = pn.config.pypic_path
    files = os.listdir(dir_)
    return files
