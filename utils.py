import math


def get_quantity_rounded(quantity, quantity_increment):

    result = 0

    if quantity_increment >= 1:
        result = int(quantity / quantity_increment) * int(quantity_increment)
    else:
        decimal_places = len(str(quantity_increment).replace("0.", ""))
        result = math.floor(quantity * 10 ** decimal_places) / (10 ** decimal_places)

    return result
