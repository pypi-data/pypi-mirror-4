import multireadline as mrl
import os
import sys

from nanotest import *

m = mrl.Multireadline()

m.add_readline(name="test1")
m.add_readline(name="test2", initlist=['a', 'b', 'c'])

# try nonexistant name
try:
    m.get("foo")
except mrl.IdMissError as err:
    pis(err.msg, "identifier 'foo' does not exist", "no such rl")
else:
    pis(0, 1, "try should not have succeeded!")

# synthetic rl switches
pis(m.options, [], "mrl's options list should be empty")
pis(m.rls["test1"]["options"], [], "test1's opt list should be empty")
pis_deeply(m.rls["test2"]["options"], ['a', 'b', 'c'], "test2's opt list should be set")
m._switchrl("test2", "NULL")
pis_deeply(m.options, ['a', 'b', 'c'], "mrl should now have test2's opt list")
m._switchrl("NULL", "test2")
pis(m.options, [], "mrl's options list should be empty again")
pis_deeply(m.rls["test2"]["options"], ['a', 'b', 'c'], "test2's opt list should be unmodified")
pis(m.rls["test1"]["options"], [], "test1's opt list should be unmodified")
m.options.append("foo")
m.options.append("bar")
pis_deeply(m.options, ["foo", "bar"], "elemnts injected into mrl's options")
m._switchrl("test1", "NULL")
pis(m.options, [], "mrl's options list should be empty again")
pis_deeply(m.rls["NULL"]["options"], ["foo", "bar"], "injected options should belong to NULL")
pis(m.rls["test1"]["options"], [], "test1's opt list should be unmodified")
m.options.append("quux")
pis(m.rls["test1"]["options"], ["quux"], "injected option")
m._switchrl("NULL", "test1")
pis_deeply(m.options, ["foo", "bar"], "mrl should have NULL's options again")
pis_deeply(m.rls["test1"]["options"], ["quux"], "test1's options")
pis_deeply(m.rls["NULL"]["options"], ["foo", "bar"], "NULL's options")
pis_deeply(m.rls["test2"]["options"], ['a', 'b', 'c'], "test2's opt list should be unmodified")


# test constraints
# redirect stdout
oldstdout = sys.stdout
tmpfile = open("/tmp/mrltest.txt", "w")
# replace the stock input with a gimmicked one
m.input = lambda arg: "fake"
# create a new rl with constraints
m.add_readline(name="test3", constrain=True, initlist=['x', 'y', 'z'], nullok=False)
try:
    sys.stdout = tmpfile
    m._getline("test3")
except mrl.BadInputError:
    sys.stdout = oldstdout
    pis(1, 1, "we shouldn't have been able to enter 'fake'")
else:
    sys.stdout = oldstdout
    pis(0, 1, "'fake' shouldn't have succeeded!")

# now try inserting a blank line
m.input = lambda arg: ""
try:
    sys.stdout = tmpfile
    m._getline("test3")
except mrl.BadInputError:
    sys.stdout = oldstdout
    pis(1, 1, "we shouldn't have been able to enter a null string either")
else:
    sys.stdout = oldstdout
    pis(0, 1, "null string shouldn't have succeeded!")

# finally, try an allowed value
m.input = lambda arg: "y"
try:
    sys.stdout = tmpfile
    m._getline("test3")
except mrl.BadInputError:
    sys.stdout = oldstdout
    pis(0, 1, "no, this should have worked")
else:
    sys.stdout = oldstdout
    pis(1, 1, "'y' should succeeded")

tmpfile.close()
os.unlink("/tmp/mrltest.txt")

nanotest_summary()
