v0.6
----

* Bugfixes
  * Issue #30 - Wrong behavior for the dependencies property validation
  * Fix a miswritten test

v0.5
----

* Bugfixes
  * Issue #17 - require path for error objects
  * Issue #18 - multiple type validation for non-objects


v0.4
----

* Preliminary support for programmatic access to error details (Issue #5).
  There are certainly some corner cases that don't do the right thing yet, but
  this works mostly.

    In order to make this happen (and also to clean things up a bit), a number
    of deprecations are necessary:
        * ``stop_on_error`` is deprecated in ``Validator.__init__``. Use 
          ``Validator.iter_errors()`` instead.
        * ``number_types`` and ``string_types`` are deprecated there as well.
          Use ``types={"number" : ..., "string" : ...}`` instead.
        * ``meta_validate`` is also deprecated, and instead is now accepted as
          an argument to ``validate``, ``iter_errors`` and ``is_valid``.

* A bugfix or two

v0.3
----

* Default for unknown types and properties is now to *not* error (consistent
  with the schema).
* Python 3 support
* Removed dependency on SecureTypes now that the hash bug has been resolved.
* "Numerous bug fixes" -- most notably, a divisibleBy error for floats and a
  bunch of missing typechecks for irrelevant properties.
