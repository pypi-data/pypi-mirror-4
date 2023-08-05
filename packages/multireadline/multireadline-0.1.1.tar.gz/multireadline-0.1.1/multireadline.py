#!/usr/bin/env python

import readline

# --------------------------------------------------------------------- Errors

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class AttributeMissingError(Error):
    """Raised when a required attribute is missing from an
    invocation. Check the 'msg' attribute for details."""
    def __init__(self, fn, attr):
        self.attr = attr
        self.msg  = "attribute '{}' missing from call to {}".format(attr, fn)

class IdMissError(Error):
    """Raised when an identifier does not exist. Check the 'msg'
    attribute for details."""
    def __init__(self, attr):
        self.msg  = "identifier '{}' does not exist".format(attr)

class IdCollisionError(Error):
    """Raised when an identifier must be unique and is not. Check the
    'msg' attribute for details."""
    def __init__(self, attr):
        self.attr = attr
        self.msg  = "identifier '{}' already exists".format(attr)

class ArgConflictError(Error):
    """Raised when conflicting pairs of arguments are set. Check the
    'msg' attribute for details."""
    def __init__(self, a, a_val, b, b_val):
        self.msg = "illegal to set {} to '{}' and {} to '{}'".format(a, a_val, b, b_val)

class BadInputError(Error):
    """Raised when an illegal value is received as user input"""
    pass

# -------------------------------------------------------------------- Classes


class Multireadline(object):
    def __init__(self):
        # this is the object that users should have a handle on. it
        # holds completer/history data
        self.rls = {}
        self.cur = None
        self.options = []
        readline.parse_and_bind('tab: complete')
        readline.set_completer(self.complete)
        return

    def add_readline(self, constrain=False, nullok=True, sub='^', **kw):
        """Create a new history/completion instance. Arguments:

        constrain : Only allow existing entries as valid inputs
        initlist  : An initial list of completions
        name      : Unique identifier of the history/completion instance (req'd)
        nullok    : The empty string is acceptable as an input value
        preprompt : Text displayed before prompt line
        prompt    : The prompt string (default: 'name >')
        sub       : Character which replaces space on input"""
        # check for pre-construction error conditions
        if 'name' not in kw:
            raise AttributeMissingError(self.add_readline.__name__, "name")
        if kw['name'] in self.rls:
            raise IdCollisionError(kw['name'])
        if constrain and nullok:
            raise ArgConflictError('constrain', constrain, 'nullok', nullok)
        if constrain and 'initlist' not in kw:
            raise ArgConflictError('constrain', constrain, 'initlist', 'None')
        # ok, build completer
        c = {}
        c['constrain'] = constrain
        c['nullok']    = nullok
        c['sub']       = sub
        c['hist']      = []
        if 'prompt' in kw:
            c['prompt'] = kw['prompt']
        else:
            c['prompt'] = "{}> ".format(kw['name'])
        if 'initlist' in kw:
            c['options'] = sorted([ x.replace(' ', sub) for x in kw["initlist"] ])
        else:
            c['options'] = []
        if 'preprompt' in kw:
            c['preprompt'] = kw["preprompt"]
        else:
            c['preprompt'] = None
        self.rls[kw['name']] = c
        self.cur = kw['name']


    def complete(self, text, state):
        response = None
        if state == 0:
            # This is the first time for this text, so build a match list.
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        # Return the state'th item from the match list, if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        return response


    def get(self, name):
        # can't call get without a name or without self.cur being set
        if not name in self.rls:
            raise IdMissError(name)
        if self.cur == None:
            raise IdMissError("current completer")
        # 1. copy readline history to self.rls[self.cur]['hist']
        c = self.rls[self.cur]
        c['hist'] = [ readline.get_history_item(i)
                      for i in range(1, readline.get_current_history_length() + 1) ]
        # 2. copy options list to self.rls[self.cur]['options']
        if len(self.options) > 0:
            c['options'] = self.options
        # 3. copy self.rls[name]['hist'] to readline history
        readline.clear_history()
        for line in self.rls[name]['hist']:
            readline.add_history(line)
        # 4. copy self.rls[name]['options'] to options list
        self.options = self.rls[name]['options']
        # 5. set self.cur = name
        self.cur = name
        # 6. get line of input (and here do checks against 
        ok = False
        while not ok:
            try:
                line = self._getline()
            except BadInputError:
                continue
            ok = True
        return line

    def _getline(self):
        c = self.rls[self.cur]
        if c['preprompt']: print(c['preprompt'])
        line = input(c['prompt'])
        line = line.strip()
        # handle substitution
        rlline = line.replace(' ', c['sub'])
        line = rlline.replace(c['sub'], ' ')
        # handle constraints
        if c['constrain']:
            if rlline not in c['options']:
                print("\nSorry, {} is not an allowed option. Please enter a new value.\n".format(line))
                raise BadInputError
        if not c['nullok'] and line == '':
            print("\nSorry, blank lines are not allowed. Please enter a new value.\n".format(line))
            raise BadInputError
        # and history munging
        readline.replace_history_item(readline.get_current_history_length() - 1, rlline)
        if rlline not in self.options and rlline != '':
            self.options.append(rlline)
            self.options = sorted(self.options)
        return line
