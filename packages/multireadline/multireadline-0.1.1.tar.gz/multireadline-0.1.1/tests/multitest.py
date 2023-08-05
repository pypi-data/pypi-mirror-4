import multireadline as mrl

from nanotest import *


m = mrl.Multireadline()
# failing add_readline() calls
try:
    m.add_readline()
except mrl.AttributeMissingError as err:
    pis(err.attr, "name", "'name' is required")
    pis(err.msg, "attribute 'name' missing from call to add_readline", "no name passed")
try:
    m.add_readline(name='foo', constrain=True)
except mrl.ArgConflictError as err:
    pis(err.msg, "illegal to set constrain to 'True' and nullok to 'True'",
        "constrain but nullok")
try:
    m.add_readline(name='foo', constrain=True, nullok=False)
except mrl.ArgConflictError as err:
    pis(err.msg, "illegal to set constrain to 'True' and initlist to 'None'",
        "constrain but no initlist")

# now a passing one
pis(len(m.rls), 0, "no instances yet")
m.add_readline(name="foo")
pis(len(m.rls), 1, "added one instance")
pis('foo' in m.rls, True, "added 'foo'")
pis(m.rls['foo']['constrain'], False, "constrain default")
pis(m.rls['foo']['nullok'], True, "nullok default")
pis(m.rls['foo']['prompt'], "foo> ", "prompt default")
pis(m.rls['foo']['preprompt'], None, "preprompt default")
pis(m.rls['foo']['options'], [], "options default")
pis(m.cur, "foo", "current rl should be foo")
# now fail to add another with same name
try:
    m.add_readline(name="foo")
except mrl.IdCollisionError as err:
    pis(err.msg, "identifier 'foo' already exists", "id collision")


nanotest_summary()
