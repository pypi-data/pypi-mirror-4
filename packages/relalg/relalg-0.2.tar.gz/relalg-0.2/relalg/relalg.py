import itertools
import operator
from collections import OrderedDict


class Relation(object):
    def __init__(self, *headers):
        self.headers = headers
        self.data = []
        self.attributes = [Attribute(name) for name in headers]
        for attr in self.attributes:
            setattr(self, attr.name, attr)

    def index_of(self, name):
        return self.headers.index(name)

    def items(self):
        return [zip(self.headers, r) for r in self.data]

    @property
    def dict(self):
        return [OrderedDict(row) for row in self.items()]


class Attribute(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self._apply_operator(operator.eq, self, other)

    def __ne__(self, other):
        return self._apply_operator(operator.ne, self, other)

    def __gt__(self, other):
        return self._apply_operator(operator.gt, self, other)

    def __lt__(self, other):
        return self._apply_operator(operator.lt, self, other)

    def __ge__(self, other):
        return self._apply_operator(operator.ge, self, other)

    def __le__(self, other):
        return self._apply_operator(operator.le, self, other)

    @staticmethod
    def _apply_operator(op, this, that):
        return lambda rel, row: op(row[rel.index_of(this.name)], row[rel.index_of(that.name)])


def rename(rename_map, rel):
    new_rel = Relation(*[rename_map.get(h, h) for h in rel.headers])
    new_rel.data = [d for d in rel.data]
    return new_rel


def project(fields, rel):
    indexes = [rel.index_of(f) for f in fields]
    new_rel = Relation(*fields)
    new_rel.data = [[r[idx] for idx in indexes] for r in rel.data]
    return new_rel


def select(predicate, rel):
    new_rel = Relation(*rel.headers)
    new_rel.data = [r for r in rel.data if predicate(rel, r)]
    return new_rel


def product(rel1, rel2):
    new_rel = Relation(*([attr.name for attr in rel1.attributes] + [attr.name for attr in rel2.attributes]))
    new_rel.data = [tuple(itertools.chain(*m)) for m in itertools.product(rel1.data, rel2.data)]
    return new_rel


def join(predicate, rel1, rel2):
    return select(predicate, product(rel1, rel2))
