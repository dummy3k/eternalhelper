def str_to_touple(map_size):
    """
        Converts a string to an integer touple.

        >>> str_to_touple('123,456')
        (123, 456)
    """
    map_size = map_size.split(',')
    return (int(map_size[0]), int(map_size[1]))
