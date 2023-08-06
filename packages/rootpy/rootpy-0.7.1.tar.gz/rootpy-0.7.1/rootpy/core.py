# Copyright 2012 the rootpy developers
# distributed under the terms of the GNU General Public License
"""
This module contains base classes defining core functionality
"""
import ROOT
import uuid


class _repr_mixin:

    def __str__(self):

        return self.__repr__()


class _copy_construct_mixin:

    def set_from(self, other):

        self.__class__.__bases__[-1].__init__(self, other)


class _resetable_mixin:

    def reset(self):

        self.__init__()


def isbasictype(thing):
    """
    Is this thing a basic builtin numeric type?
    """
    return isinstance(thing, (float, int, long))


class Object(object):
    """
    Overrides TObject methods. Name and title for TObject-derived classes
    are optional. If no name is specified, a UUID is used to ensure uniqueness.
    """
    def __init__(self, name, title, *args, **kwargs):

        if name is None:
            name = uuid.uuid4().hex
        if title is None:
            title = ""
        self.ROOT_base.__init__(
                self, name, title, *args, **kwargs)

    @property
    def ROOT_base(self):
        """
        Return the ROOT base class. In rootpy all derived classes must list the
        ROOT base class as the last class in the inheritance list.

        This is not a @classmethod due to how the Hist classes are wrapped
        """
        return self.__class__.__bases__[-1]

    def Clone(self, name=None, title=None, **kwargs):

        if name is not None:
            clone = self.ROOT_base.Clone(self, name)
        else:
            clone = self.ROOT_base.Clone(self, uuid.uuid4().hex)
        # cast
        clone.__class__ = self.__class__
        if title is not None:
            clone.SetTitle(title)
        if hasattr(clone, "_post_init"):
            from .plotting.core import Plottable
            if isinstance(self, Plottable):
                kwds = self.decorators
                kwds.update(kwargs)
                clone._post_init(**kwds)
            else:
                clone._post_init(**kwargs)
        return clone

    @property
    def name(self):

        return self.GetName()

    @name.setter
    def name(self, _name):

        self.SetName(_name)

    @property
    def title(self):

        return self.GetTitle()

    @title.setter
    def title(self, _title):

        self.SetTitle(_title)

    def __copy__(self):

        return self.Clone()

    def __deepcopy__(self, memo):

        return self.Clone()

    def __repr__(self):

        return self.__str__()

    def __str__(self):

        return "%s('%s')" % (self.__class__.__name__, self.GetName())


class NamelessConstructorObject(Object):
    """
    Handle special cases like TGraph where the
    ROOT constructor does not take name/title
    """
    def __init__(self, name, title, *args, **kwargs):

        if name is None:
            name = uuid.uuid4().hex
        if title is None:
            title = ""
        self.ROOT_base.__init__(self, *args, **kwargs)
        self.SetName(name)
        self.SetTitle(title)
