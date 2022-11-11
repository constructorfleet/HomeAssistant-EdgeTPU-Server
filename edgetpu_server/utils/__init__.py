from typing import List, Union, Tuple


def flatten(nested_list: List[Union[List, Tuple]]) -> List:
    """Flattens a list of lists/tuples."""
    return [
        item
        for sublist
        in nested_list
        for item
        in sublist
    ]
