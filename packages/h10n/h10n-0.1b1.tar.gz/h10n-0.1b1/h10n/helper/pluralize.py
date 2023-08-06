class Pluralize(object):

    def __init__(self, lang, country):
        self._call = getattr(self, lang)

    def __call__(self, count):
        return self._call(count)

    def en(self, count):
        return 0 if count == 1 else 1

    def ru(self, count):
        mod10 = count % 10
        mod100 = count % 100
        if mod10 == 1 and mod100 != 11:
            return 0
        elif mod10 >= 2 and mod10 <= 4 and (mod100 < 10 or mod100 >= 20):
            return 1
        else:
            return 2
