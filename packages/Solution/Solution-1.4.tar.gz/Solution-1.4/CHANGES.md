# Solution Changelog

## 1.4

- Validators now take a `form` argument.
- `Date` form field handling of datetime and dates.

## 1.3

- Fix bug with date formatting.

## 1.2

- Minor bugfixes.

## 1.1.16

- When the forms of a `FormSet` have a defined model, the objects without user data are collected at `FormSet.missing_objs` list, so the user can delete them or set a flag or something similar.

- Stronger `FormSet` new forms detection: it no longer depends of a "first field" available, but any field is now enough.

## 1.1.15

- An empty data value is returned as `None` instead of `u''`.

