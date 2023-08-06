import random
import _chemfp


ids = [1,2,3,2,1,2,3,2,1]
#ids = range(10)
scores = [0.6, 0.4, 0.5, 0.2, 0.8, 0.7, 0.7, 0.0, 1.0]
#scores = [random.random() for id in ids]
assert len(scores) == len(ids)

I = range(len(ids))
values = zip(ids, scores)

def load():
    x = _chemfp.SearchResults(1)
    for value in values:
        x._add_hit(0, *value)
    return x

x = load()
print dir(x)

assert list(x._get_scores(0)) == scores

x.reorder_all("increasing-score")
assert list(x._get_scores(0)) == sorted(scores)
expect = [ids[i] for i in sorted(I, key=lambda i: (scores[i], ids[i]))]
assert list(x._get_indices(0)) == expect, (
    list(x._get_indices(0)), expect)
'''
x = load()
x.reorder_all("decreasing-score")
assert list(x._get_scores(0)) == sorted(scores)[::-1]
expect = [ids[i] for i in sorted(I, key=lambda i: (-scores[i], ids[i]))]
assert list(x._get_indices(0)) == expect

x = load()
x.reorder_all("increasing-index")
assert list(x._get_indices(0)) == sorted(ids), (list(x._get_indices(0)), sorted(ids))

x = load()
x.reorder_all("decreasing-index")
assert list(x._get_indices(0)) == sorted(ids)[::-1]

'''
