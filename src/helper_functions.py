def try_convert_to_float(string):
    """For parsing options like 0/0.5, 1/1.5 etc
    If string is normal number returns normal float
    If string can't be parsed returns string"""
    try:
        number = float(string)
    except ValueError:
        if string.find('/') != -1:
            numbers = [float(x) for x in
                      string.split('/')]
            number = numbers[0] + (
                    (numbers[1] - numbers[0]) / 2)
        else:
            return string
    if number == 0.0:
        number = 0
    return number


def is_element_empty(element):
    """Check text attribute of element to determine if element is empty"""
    return element.text == '' or element.text.replace(' ', '') == ''
