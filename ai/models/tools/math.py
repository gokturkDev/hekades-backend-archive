def add(number_1, number_2):
    """
    Sums two numbers

    Parameters
    ----------
    number_1 : number
        the first number
    number_2 : number
        the second number

    Returns
    -------
    number
        The result of addition
    """
    return number_1 + number_2


def substitute(number_to_substitute_from, number_to_substitute):
    """
    Substitutes a number from another

    Parameters
    ----------
    number_to_substitute_from : number
        number to substitute from
    number_to_substitute : number
        number_to_substitute

    Returns
    -------
    number
        The result of substitution
    """
    return number_to_substitute_from - number_to_substitute


def multiply(number_1, number_2):
    """
    Multiplies two Numbers

    Parameters
    ----------
    number_1 : number
        the first number
    number_2 : number
        the second number

    Returns
    -------
    number
        The result of multiplication
    """
    return number_1 * number_2


def divide(dividend, divisor):
    """
    Divides two Numbers

    Parameters
    ----------
    dividend : number
        the dividend
    divisor : number
        the divisor

    Returns
    -------
    number
        The result of the division
    """

    return dividend / divisor


def round_number(number, ndigits):
    """
    Round a number to specified number of digits

    Parameters
    ----------
    number : number
        number to be rounded
    ndigits : integer
        number of digits to round up to i.e precision

    Returns
    -------
    number
        The result of rounding
    """
    return round(number, ndigits=ndigits)
