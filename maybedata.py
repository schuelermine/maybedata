"""A Python implementation of a Maybe type that represents potentially missing values"""

from __future__ import annotations
from abc import abstractmethod
from callableabc import CallableABC
from collections.abc import Callable, Iterator
from typing import Generic, NoReturn, Optional, TypeVar, cast, overload

__version__ = "0.3"

__all__ = ("Maybe", "Just", "Nothing", "MissingValueError")

T = TypeVar("T", covariant=True)
G = TypeVar("G")
U = TypeVar("U")
V = TypeVar("V")


class Maybe(CallableABC, Generic[T]):
    """
    Callable abstract base class for Just and Nothing.
    A Maybe value represents a value that may or may not exist.
    To construct a Just, call Maybe with one argument.
    To construct a Nothing, call Maybe with no arguments.
    Calling Maybe does not construct a direct instance of Maybe.
    Property Maybe.present indicates if a value is present.
    Property Maybe.value is the value if it is present.
    To override the constructors used for the static methods when inheriting, redefine `_class_call` in your class to match the behavior of Maybe().
    Just and Nothing support pattern matching.
    See also: Just, Nothing
    """

    __slots__ = ("present", "value")

    present: bool
    value: Optional[T]

    @overload
    @classmethod
    def _class_call(cls, arg: G, /) -> Just[G]:
        ...

    @overload
    @classmethod
    def _class_call(cls) -> Nothing:
        ...

    @classmethod
    def _class_call(cls, *args: G) -> Maybe[G]:
        argc = len(args)
        if argc > 1:
            raise TypeError(
                f"Maybe() takes up to one positional argument, but {argc} were given"
            )
        if argc == 0:
            return Nothing()
        return Just[G](args[0])

    def assume_present(self) -> T:
        """
        Return the value, assuming it exists.
        Raises MissingValueError if value is missing.
        """
        if self.present:
            return cast(T, self.value)
        else:
            raise MissingValueError(f"{self!r} is a missing value")

    @abstractmethod
    def get(self: Maybe[G], /, default: G) -> G:
        """
        Return the value if it is present, otherwise, return default.
        """
        pass

    @abstractmethod
    def map(self: Maybe[G], f: Callable[[G], U], /) -> Maybe[U]:
        """
        Apply a function on the value, if it exists.
        Returns a new Maybe value containing the transformed value, if a value was present.
        """
        pass

    @abstractmethod
    def replace(self: Maybe[object], value: U, /) -> Maybe[U]:
        """
        Replace the value with a new value, if it exists.
        Returns a new Maybe value containing the new value, if a value was present.
        maybe.replace(value) is equivalent to maybe.map(lambda _: value).
        """
        pass

    @abstractmethod
    def then(self: Maybe[object], maybe: Maybe[U], /) -> Maybe[U]:
        """
        Replace a Maybe value with another Maybe value, if the first value is present.
        Returns the passed second Maybe value, unless the first value is missing.
        maybe1.then(maybe2) is equivalent to maybe1.bind(lambda _: maybe2).
        """
        pass

    @abstractmethod
    def alternatively(self: Maybe[G], maybe: Maybe[G], /) -> Maybe[G]:
        """
        Replace a Maybe value with another Maybe value, if the first value is not present.
        Returns the passed second Maybe value, unless the first value is present.
        """
        pass

    @abstractmethod
    def bind(self: Maybe[G], f: Callable[[G], Maybe[U]], /) -> Maybe[U]:
        """
        Construct a new Maybe value with the value in the first Maybe value, if it exists.
        Calls the passed function on the value, returning the result, if the value is present.
        maybe.bind(f) is equivalent to maybe.map(f).join().
        """
        pass

    @abstractmethod
    def join(self: Maybe[Maybe[G]]) -> Maybe[G]:
        """
        Flatten a Maybe value potentially containing another Maybe value.
        Returns the value, if it exists, and a missing value otherwise.
        maybe.join() is equivalent to maybe.bind(lambda x: x).
        """
        pass

    @abstractmethod
    def ap(self: Maybe[Callable[[G], U]], maybe: Maybe[G], /) -> Maybe[U]:
        """
        Apply a function from inside a Maybe value onto the value in another Maybe value, if both exist.
        Returns a missing value if any of the Maybe operands is missing.
        maybe1.ap(f, maybe2) is equivalent to maybe1.flatmap(lambda f: maybe2.flatmap(lambda x: f(x)))
        """
        pass

    @classmethod
    def lift2(
        cls, f: Callable[[G, U], V], maybe1: Maybe[G], maybe2: Maybe[U]
    ) -> Maybe[V]:
        """
        Apply a function over two Maybe values, returning a missing value if any inputs were missing.
        Maybe.lift2(f, maybe1, maybe2) is equivalent to maybe1.map(lambda x: lambda y: f(x, y)).ap(maybe2)
        """
        return maybe1.map(lambda x: lambda y: f(x, y)).ap(maybe2)

    @classmethod
    def lift(cls: type[Maybe[G]], f: Callable[..., G], *args: Maybe[object]) -> Maybe[G]:
        """
        Apply a function that takes multiple arguments over multiple Maybe values, returning a missing value if any inputs were missing.
        This is a general version of Maybe.lift2.
        """
        values: list[object] = []
        is_missing = False
        for maybe in args:
            if maybe.present:
                values.append(maybe.value)
            else:
                is_missing = True
                break
        if is_missing:
            return cls._class_call()
        else:
            return cls._class_call(f(*values))

    @classmethod
    def from_optional(cls: type[Maybe[G]], value: Optional[G], /) -> Maybe[G]:
        """
        Create a Maybe value from a value that is potentially None.
        Returns a present value if value is not None, else returns a missing value.
        """
        if value is None:
            return cls._class_call()
        else:
            return cls._class_call(value)

    @classmethod
    def with_bool(cls: type[Maybe[G]], present: bool, value: G) -> Maybe[G]:
        """
        Create a Maybe value from a value and a boolean.
        Returns a missing value if present is False, else returns a present value.
        """
        if present:
            return cls._class_call(value)
        else:
            return cls._class_call()

    def __or__(self: Maybe[G], other: Maybe[G]) -> Maybe[G]:
        return self.alternatively(other)

    def __rshift__(self: Maybe[object], other: Maybe[U]) -> Maybe[U]:
        return self.then(other)


class Just(Maybe[T]):
    """
    Subclass of Maybe that indicates a value is present.
    Construct with one value: Just(value)
    Property Just.present is always True.
    Property Just.value is the value.
    Just(value) is supported in pattern matching.
    See also: Maybe, Nothing
    """

    __slots__ = ("present", "value")

    value: T

    def __init__(self: Just[T], value: T, /) -> None:
        self.present = True
        self.value = value

    def get(self: Maybe[G], /, default: G) -> G:
        return cast(G, self.value)

    def map(self: Just[G], f: Callable[[G], U], /) -> Just[U]:
        return Just(f(self.value))

    def replace(self: Just[object], value: U, /) -> Just[U]:
        return Just(value)

    def then(self: Just[object], maybe: Maybe[U]) -> Maybe[U]:
        return maybe

    def alternatively(self: Just[G], maybe: Maybe[object], /) -> Maybe[G]:
        return self

    def bind(self: Just[G], f: Callable[[G], Maybe[U]], /) -> Maybe[U]:
        return f(self.value)

    def join(self: Just[Maybe[G]]) -> Maybe[G]:
        return self.value

    def ap(self: Just[Callable[[G], U]], maybe: Maybe[G]) -> Maybe[U]:
        return maybe.map(self.value)

    def __repr__(self: Just[object]) -> str:
        return f"Just({self.value!r})"

    def __eq__(self: Just[object], other: object) -> bool:
        if isinstance(other, Just):
            return bool(self.value == other.value)
        elif isinstance(other, Nothing):
            return False
        else:
            return NotImplemented

    def __hash__(self: Just[object]) -> int:
        return hash((self.value, self.present))

    def __bool__(self: Just[object]) -> bool:
        return True

    def __len__(self: Just[object]) -> int:
        return 1

    def __iter__(self: Just[G]) -> Iterator[G]:
        return iter((self.value,))

    def __contains__(self, item: object) -> bool:
        return self.value == item

    __match_args__ = ("value",)


class MissingValueError(ValueError):
    "Raised to indicate a potentially missing value was missing."
    pass


class Nothing(Maybe[NoReturn]):
    """
    Subclass of Maybe that indicates a value is missing.
    Construct with no value: Nothing()
    Property Nothing.present is always False.
    Property Nothing.value is always None.
    Nothing() is supported in pattern matching.
    See also: Maybe, Just
    """

    __slots__ = ("present", "value")

    def __init__(self: Nothing) -> None:
        self.present = False
        self.value = None

    def get(self: Nothing, /, default: G) -> G:
        return default

    def map(self: Nothing, f: Callable[[NoReturn], object], /) -> Nothing:
        return Nothing()

    def replace(self: Nothing, value: object, /) -> Nothing:
        return Nothing()

    def then(self: Nothing, maybe: Maybe[object], /) -> Nothing:
        return Nothing()

    def alternatively(self: Nothing, maybe: Maybe[G], /) -> Maybe[G]:
        return maybe

    def bind(self: Nothing, f: Callable[[NoReturn], Maybe[object]], /) -> Nothing:
        return Nothing()

    def join(self: Nothing) -> Nothing:
        return Nothing()

    def ap(self: Nothing, maybe: Maybe[object]) -> Nothing:
        return Nothing()

    def __repr__(self: Nothing) -> str:
        return "Nothing()"

    def __eq__(self: Nothing, other: object) -> bool:
        if isinstance(other, Nothing):
            return True
        elif isinstance(other, Just):
            return False
        else:
            return NotImplemented

    def __hash__(self: Nothing) -> int:
        return hash(())

    def __bool__(self: Nothing) -> bool:
        return False

    def __len__(self: Nothing) -> int:
        return 0

    def __iter__(self: Nothing) -> Iterator[NoReturn]:
        return iter(())

    def __contains__(self, item: object) -> bool:
        return False

    __match_args__ = ()
