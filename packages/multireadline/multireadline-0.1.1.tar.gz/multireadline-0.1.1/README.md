Multireadline
=============

A wrapper around Python's readline module which makes it easy to have
an arbitrary number of "inputs", each with its own history


Basic Usage
-----------

```
import multireadline as mrl

m = mrl.Multireadline()

m.add_readline(name="band")
m.add_readline(name="album")
m.add_readline(name="year")

while True:
    m.get("band")
    m.get("album")
    m.get("year")
```

Each of the three calls to `get()` will have their own history,
tab-completion lists, and prompts, which will be shown by letting the
loop run for several iterations.

Calls to `add_readline()` may raise exceptions (see below).

### _Nota Bene_

Since `multireadline` is built atop the standard Python bindings for
readline, it does not handle spaces in inputs well. As a workaround,
the internal input list substitutes another character (by default, a
caret) anywhere that a space occurs. So if I enter

`band> Three Dog Night`

then, while my program would get `Three Dog Night` as my input, the
readline history would store`Three^Dog^Night`. This workaround lets
tab-completion work "the right way".

This is an unbeautiful, ungraceful hack, but I'd rather have that (and
working code) than spend several weeks digging into the innards of
readline (without working code).


Options
-------

Calls to `add_readline()` can take several arguments. The only
required one is `name`, which sets the identifier (and default prompt)
of the readline instance being added. The others are:

* `constrain` (boolean)

* `initlist` (list) - Initial list of 

* `nullok` (boolean) - Allow/disallow blank lines as valid input

* `preprompt` (string) - Text printed _before_ the prompt line

* `prompt` (string) - Text displayed as the input prompt

* `sub` (string) - Character to be substituted for space in readline history


Exceptions
----------

* `AttributeMissingError` - raised when `name` (or other required
attribute) is not included in a call.

* `IdMissError` - Raised when a name lookup fails

* `IdCollisionError` - Raised when a specified name conflicts with an existing (unique) name

* `ArgConflictError` - Raised when incompatible/impossible argument combinations are given

