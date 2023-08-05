import multireadline as mrl

from nanotest import *

m = mrl.Multireadline()

# failing add_readline() calls
try:
    m.add_readline()
except mrl.AttributeMissingError as err:
    pis(err.attr, "name", "'name' is required")
    pis(err.msg, "attribute 'name' missing from call to add_readline", "no name passed")
else:
    pis(0, 1, "try should not have succeeded!")

try:
    m.add_readline(name='foo', constrain=True, nullok=False)
except mrl.ArgConflictError as err:
    pis(err.msg, "illegal to set constrain to 'True' and initlist to 'None'",
        "constrain but no initlist")
else:
    pis(0, 1, "try should not have succeeded!")


# now a passing one
pis(len(m.rls), 1, "only NULL should exist")
m.add_readline(name="foo")
pis(len(m.rls), 2, "added one instance")
pis('foo' in m.rls, True, "added 'foo'")
pis(m.rls['foo']['constrain'], False, "constrain default")
pis(m.rls['foo']['nullok'], True, "nullok default")
pis(m.rls['foo']['prompt'], "foo> ", "prompt default")
pis(m.rls['foo']['preprompt'], None, "preprompt default")
pis(m.rls['foo']['options'], [], "options default")
# now fail to add another with same name
try:
    m.add_readline(name="foo")
except mrl.IdCollisionError as err:
    pis(err.msg, "identifier 'foo' already exists", "id collision")
else:
    pis(0, 1, "try should not have succeeded!")

try:
    m.add_readline(name='bar', constrain=True, initlist=[])
except mrl.ArgConflictError as err:
    pis(0, 1, "this should work. got err: {}".format(err.msg))
else:
    pis(m.rls["bar"]["nullok"], False, "nullok should be auto switched off")


# initlist
m.add_readline(name="baz", initlist=['a', 'b', 'the cat'])
pis_deeply(m.rls["baz"]["options"], ['a', 'b', 'the^cat'], "options should be populated")

nanotest_summary()
