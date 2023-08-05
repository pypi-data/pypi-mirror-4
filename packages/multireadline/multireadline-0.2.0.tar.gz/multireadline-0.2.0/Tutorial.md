Multireadline Tutorial
======================

The goal of multireadline is to make far richer command-line tools
possible with very low programmer overhead. You get multiple "inputs",
each with its own history. These histories can be:

* paged though with up/down arrows or `C-p`/`C-n`
* incrementally searched with `C-r`
* tab-completed, with partial-completions

and each is independent of the others, so each input field you give
history support to builds up its _own_ history.


Getting started
---------------

Import the module and instantiate a multireadline object:

```
import multireadline as mrl

m = mrl.Multireadline()
```

Then, for any distinct user input you want to have, call
`add_readline()`. If I'm making a simple database loader script for my
music library, I might be entering bands, albums, and record labels.

```
m.add_readline(name="band")
m.add_readline(name="album")
m.add_readline(name="label")
```

This creates three histories. To use them, later in my program, I
might do:

```
band  = m.get("band")
album = m.get("album")
label = m.get("label")
```

The calls to `get()` ask the user for input, setting a prompt based on
the input name. When I ran this, I would see:

```
band> AC/DC
album> Back In Black
label> Atlantic
```

The next CD in my stack is The Temptations, _Psychedelic Soul_, on
Motown, so I enter its data. After that is AC/DC's _Highway to Hell_;
this time, all I have to type is:

```
band> A[TAB]
album> Highway to Hell
label> A[TAB]
```

and `band` would get completed to "AC/DC", while `album` would get
completed to "Atlantic". I could also have arrowed-up through history,
or done a search with `C-r`.

### An aside: the NULL input

There is an additional input, named "NULL" built into
multireadline. It's there because when `readline` is in use (and
multireadline is built on top of readline), all calls to Python's
`input()` function are intercepted by readline. NULL exists to absorb
the data from these calls and keep it separate from all your defined
multireadline inputs.

This means that when using multireadline, calls to `input()` get
history functions as well, but unlike the defined multireadline inputs
accessed via `get()`, they share a common history.


Prepopulating history
---------------------

If I'm working with an existing dataset, then it's reasonable to want
to not have to type in data that the system already knows
about. Multireadline supports this via the `initlist`
argument. Assuming that I've queried an existing database and have
generated a list of all known bands, I can do:

```
m.add_readline(name="band", initlist=bandlist)
```

and my `band` input will begin its life knowing every element of
`bandlist`.


Not taking no answer for an answer
----------------------------------

Sometimes it's ok for a user go just hit enter, giving a null
answer. Sometimes it isn't. You can tell multireadline to disallow
this.

```
m.add_readline(name="band", nullok=False)
```

Now, if I try entering a blank band name, this happens:

```
band> [ENTER]

Sorry, blank lines are not allowed. Please enter a new value.

band> 
```


Only allowing existing values
-----------------------------

The `initlist` argument can be combined with the `constrain` argument
to create an input which only allows values that it already knows
about.

```
m.add_readline(name="band", constrain=True, initlist=["AC/DC", "The Temptations"])
```

Now I have an input which will accept no value except AC/DC or The Temptations.

```
band> Foo Fighters

Sorry, Foo Fighters is not an allowed option. Please enter a new value.

band> The Temptations
album>
```

Wrapup
------

There you have it. Multireadline lets you write tools with rich input
handling, with very little effort and no dependencies.

I hope you find it useful. Bug reports, patches, questions, and
comments gladly accepted.

Write to: Shawn Boyette, <shawn@firepear.net>
