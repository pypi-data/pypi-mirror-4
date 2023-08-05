#This file is part of banknumber. The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
'''
Check the Bank code depending on the country
'''
__version__ = '1.0'

def countries():
    '''
    Return the list of country's codes that have check function
    '''
    res = [x.replace('check_code_', '').upper() for x in globals()
            if x.startswith('check_code_')]
    res.sort()
    return res

def check_code_es(number):
    '''
    Check Spanish Bank code.
    '''
    def get_control(ten_digits):
        values = [1, 2, 4, 8, 5, 10, 9, 7, 3, 6];
        value = ten_digits
        control = 0;
        for i in range(10):
            control += int(int(value[i]) * values[i])
        control = 11 - (control % 11)
        if control == 11: 
            control = 0
        elif control == 10:
            control = 1
        return control;

    if len(number) !=20 or not number.isdigit():
        return False

    value = '00'+ number[0:8]
    d1 = get_control(value);
    if d1 != int(number[8]):
        return False

    value = number[10:20]
    d2 = get_control(value);
    if d2 != int(number[9]):
        return False

    return True

def check_code(country, account):
    '''
    Check bank code for the given country which should be a 
    two digit ISO 3166 code.
    '''
    try:
        checker = globals()['check_code_%s' % country.lower()]
    except KeyError:
        return False
    return checker(account)
