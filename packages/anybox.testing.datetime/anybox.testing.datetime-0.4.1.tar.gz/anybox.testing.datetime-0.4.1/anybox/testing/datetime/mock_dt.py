# The current module will entirely substitute datetime, hence:
from datetime import *  # noqa
from datetime import datetime as original_datetime


class ReplacementSubclassMeta(type):
    """A metaclass for classes that subclass a given one to replace it.

    Usually, internal methods of the original class (or of the same module)
    will return instances of the original class directly. This meta-class
    makes it so that ``isinstance`` (resp. ``isssubclass``) does not fail for
    instances of the original class (resp. the original class).

    The replacement subclass is expected to have an ``__original_class__``
    attribute or to inherite the original class in latest position.
    """

    @classmethod  # dont' want to pollute the classes themselves
    def get_original_class(mks, cls):
        orig = getattr(cls, '___original_class__', None)
        if orig is not None:
            return orig
        bases = cls.__bases__
        if not bases:
            return
        return bases[-1]

    def __instancecheck__(cls, instance):
        return isinstance(instance, cls.get_original_class(cls))

    def __subclasscheck__(cls, subcls):
        return issubclass(subcls, cls.get_original_class(cls))


class datetime(original_datetime):

    __metaclass__ = ReplacementSubclassMeta

    _current_now = None

    @classmethod
    def now(cls, *a):
        now = cls._current_now
        if now is not None:
            # TODO timezone treatment
            return cls._current_now
        return original_datetime.now(*a)

    @classmethod
    def set_now(cls, value):
        """Change the value of now.

        On may give None as a value to get back to system clock."""
        cls._current_now = value

    @classmethod
    def real_now(cls):
        """Get back to the real meaning of now.

        This should be used once the test needing to play with current
        date/time is over. Lots of other tests may fail if on a frozen value
        of 'now'.
        """
        cls.set_now(None)
