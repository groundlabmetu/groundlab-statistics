from operator import eq


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def count_iterable(i):
    return sum(1 for e in i)


def count_unique_iterable(i):
    return len(set(i))


def filter_count(l, key, value, filter_func=eq):
    return count_iterable(filter2(l, key, value, filter_func))


def filter2(l, key, value, filter_func=eq):
    return filter(lambda x: filter_func(x[key], value), l)


def histogram(l):
    l = list(l)
    unique = list(set(l))
    return dict(zip(unique, map(lambda i: list.count(l, i), unique)))


def reverse_dict(d):
    return {v: k for k, v in d.items()}
