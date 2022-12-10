# maybedata

This is a package that implements a Maybe data type in Python that represents values that might or might not exist.

It is implemented as a class hierarchy with an abstract base class `Maybe`. This class is not constructible, but can be called to construct members of its subclasses, `Just` and `Nothing`.

All methods are documented, feel free to call `help()` on the classes!

Call `Maybe(value)` or `Just(value)` to create a value that is present.

Call `Maybe()` or `Nothing()` to create a missing value.

Check `maybe.present` to find out if a value is present.

Access `maybe.value` to get the value if it is present.

Call `maybe.assume_present()` to raise an exception if the value is not present.

Call `maybe.get(default)` to get the value or a default value.

`Maybe` and `Just` are generic classes if you use type hinting.

`Just` and `Nothing` support pattern matching.

`Maybe`, `Just`, and `Nothing` support `len()`, `bool()`, `hash()`, `iter()`, `in`, and `==`.

The method `maybe.alternatively()` can be expressed using `|`.

The method `maybe.then()` can be expressed using `>>`.
