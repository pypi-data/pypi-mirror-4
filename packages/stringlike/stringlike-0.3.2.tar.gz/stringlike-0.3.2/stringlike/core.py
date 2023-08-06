"""
Contains classes to help other classes mimic the behavior of strings.
"""


class StringLike(object):
    """
    Class to mimic the behavior of a regular string. Classes that inherit (or mixin) this class
    must implement the `__str__` magic method. Whatever that method returns is used by the various
    string-like methods.
    """

    def __getattr__(self, attr):
        """
        Forwards any non-magic methods to the resulting string's class. This allows support for
        string methods like `upper()`, `lower()`, etc.
        """
        string = str(self)
        if hasattr(string, attr):
            return getattr(string, attr)
        raise AttributeError(attr)

    def __len__(self):
        return len(str(self))

    def __getitem__(self, key):
        return str(self)[key]

    def __iter__(self):
        return iter(str(self))

    def __contains__(self, item):
        return item in str(self)

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)

    def __mul__(self, other):
        return str(self) * other

    def __rmul__(self, other):
        return other * str(self)

    def __lt__(self, other):
        return str(self) < other

    def __le__(self, other):
        return str(self) <= other

    def __eq__(self, other):
        return str(self) == other

    def __ne__(self, other):
        return str(self) != other

    def __gt__(self, other):
        return str(self) > other

    def __ge__(self, other):
        return str(self) >= other
