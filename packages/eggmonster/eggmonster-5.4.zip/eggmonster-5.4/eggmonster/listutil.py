def partition_list(l, pivot):
    """
    Like str.partition, but for lists.

    >>> sample = ['a', 'b', 'c', 'd']
    >>> partition_list(sample, 'c')
    (['a', 'b'], ['c'], ['d'])
    >>> partition_list(sample, 'd')
    (['a', 'b', 'c'], ['d'], [])
    >>> partition_list(sample, 'missing')
    (['a', 'b', 'c', 'd'], [], [])
    >>> partition_list(sample+sample, 'a')
    ([], ['a'], ['b', 'c', 'd', 'a', 'b', 'c', 'd'])
    """
    try:
        pivot_index = l.index(pivot)
        return l[:pivot_index], [l[pivot_index]], l[pivot_index+1:]
    except ValueError:
        return l, [], []

def rpartition_list(l, pivot):
    """
    Like str.rpartition, but for lists.

    >>> sample = ['a', 'b', 'c', 'd']
    >>> rpartition_list(sample, 'c')
    (['a', 'b'], ['c'], ['d'])
    >>> rpartition_list(sample, 'a')
    ([], ['a'], ['b', 'c', 'd'])
    >>> rpartition_list(sample, 'missing')
    ([], [], ['a', 'b', 'c', 'd'])
    >>> rpartition_list(sample+sample, 'a')
    (['a', 'b', 'c', 'd'], ['a'], ['b', 'c', 'd'])
    """
    try:
        pivot_index = len(l) - list(reversed(l)).index(pivot) - 1
        return l[:pivot_index], [l[pivot_index]], l[pivot_index+1:]
    except ValueError:
        return [], [], l
