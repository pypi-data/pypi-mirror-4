def flatten(x, y):
    return float(x+y)/2

def median(iterable, flatten_func=flatten):
    if not len(iterable):
        return None

    center = len(iterable)/2
    sorted_list = sorted(iterable)

    if len(sorted_list) % 2:
        return sorted_list[center]
    else:
        return flatten_func(sorted_list[center-1], sorted_list[center])