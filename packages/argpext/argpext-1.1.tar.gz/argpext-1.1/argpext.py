#!/usr/bin/env python3

"""

Argpext: Hierarchical argument processing based on argparse.

Copyright (c) 2012 by Alexander V. Shirokov. This material
may be distributed only subject to the terms and conditions
set forth in the Open Publication License, v1.0 or later
(the latest version is presently available at
http://www.opencontent.org/openpub ).


"""

import sys
import time
import os
import argparse
import abc
import collections


class InitializationError(Exception): pass
class KeyEvaluationError(Exception): pass


class BaseNode(object):

    def _log(self,prog,args):
        """Update the history file, if one if defined."""
        filename = histfile()

        if not len(args): return

        if filename is not None:

            # Generate the logline
            timestr = time.strftime('%Y%m%d-%H:%M:%S', time.localtime())
            path = os.getcwd()
            cmd = ' '.join([prog]+args)


            logline = ','.join([ timestr, path, cmd ])+'\n'

            # Update the log file
            with open(filename,'a') as fho:
                fho.write( logline )

            # Truncate history file, if necesary
            size = os.stat(filename).st_size

            def histmaxsize():
                "Returns maximum size of history file (if any), in bytes."
                minsize = 10*1024
                q = os.getenv('ARGPEXT_HISTORY_MAXSIZE')
                q = minsize if q is None else max(int(q),minsize)
                return q

            maxsize = histmaxsize()
            if size > maxsize:
                cutsize = size-maxsize/2
                remainder = ''
                with open(filename) as fhi:
                    cur = 0
                    while 1:
                        line = fhi.readline()
                        cur += len(line)
                        if cur >= cutsize: break
                    remainder = fhi.read()
                with open(filename,'w') as fhi:
                    fhi.write(remainder)


class Function(BaseNode):
    """Base class for command line interface to a Python function."""

    def populate(self,parser):
        """This method should be overloaded if HOOK takes
        positive number of arguments. The argument must be
        assumed to be of argparse.ArgumentParser type. For
        each argument X of the HOOK method there must be a
        call (or its equivalent) to the parser.add_argument
        method with dest='X'."""
        pass

    def defaults(self):
        """Returns the dictionary of command line default
        values of arguments."""
        parser = argparse.ArgumentParser()
        self.populate( parser )
        vars = {}
        for k,v in parser._option_string_actions.items():
            if issubclass(type(v),argparse.Action):
                if isinstance(v,argparse._HelpAction): continue
                key = v.dest
                value = v.default
                vars[key] = value
        return vars

    def __callable(self):
        q = type(self).HOOK
        return q.__func__ if sys.version_info[0:2] <= (2, 7,) else q

    def __call__(self,*args,**kwds):
        """Execute the reference function based on command line
        level default values of arguments and the values
        *args* and *kwds* given in the argument list. The
        return value is identical to the return value of the
        reference function."""
        kwds0 = self.defaults()
        for key,value in kwds.items():
            kwds0[key] = value
        return self.__callable()(*args,**kwds0)

    def digest(self,prog=None,args=None):
        """Execute the reference function based on command line
        argument *args*, which must be 
        :py:class:`list`, :py:class:`tuple`, or *None* (in
        which case it is automatically assigned to
        `=sys.argv[1:]`). The return value is identical to
        the return value of the reference function.
        """
        if prog is None: prog = os.path.basename( sys.argv[0] )
        if args is None: args = sys.argv[1:]
        BaseNode._log(self,prog=prog,args=args)

        q = self.__doc__
        if q is None: q = self.HOOK.__doc__
        q = argparse.ArgumentParser(  description=q )
        self.populate( q )
        q = argparse.ArgumentParser.parse_args(q,args)
        q = vars(q)
        return self.__callable()( **q )


class Node(BaseNode):
    """Command line interface for a node."""

    def digest(self,prog=None,args=None):
        """Execute the node based on command line
        argument *args*, which must be 
        :py:class:`list`, :py:class:`tuple`, or *None* (in
        which case it is automatically assigned to
        `=sys.argv[1:]`). The return value is identical to
        the return value of the reference function.
        """

        if prog is None: prog = os.path.basename( sys.argv[0] )
        if args is None: args = sys.argv[1:]

        _EXTRA_KWD = '_ARGPEXT_EXTRA_KWD'


        # Write history file
        if not hasattr(self,'_internal'):
            BaseNode._log(self,prog=prog,args=args)


        #print('(%s)' % prog)

        parser = argparse.ArgumentParser( prog=prog, description=self.__doc__  )
        nodes = {}
        subparsers = None

        attributename = 'SUBS'
        subs = getattr(self,attributename,None)
        if subs is None:
            raise InitializationError('mandatory attribute %s is not defined for class %s' % (  attributename , type(self).__name__ ) )


        for name,node in subs:
            nodes[name] = node

            def binding(namespace):
                if not isinstance(namespace,argparse.Namespace): raise TypeError
                q = vars( namespace )
                del q[ _EXTRA_KWD ]
                return node.HOOK( **q )

            if subparsers is None: subparsers = parser.add_subparsers(help='Description')

            dosctr = getattr(node,'__doc__',None)

            if issubclass(node,Function):
                if dosctr is None: dosctr = node.HOOK.__doc__
                subparser = subparsers.add_parser(name,help=dosctr,description=dosctr )
                node().populate( subparser )
                subparser.set_defaults( ** { _EXTRA_KWD : binding } )
            elif issubclass(node,Node):
                N = node()
                N._internal = True
                subparser = subparsers.add_parser(name,help=dosctr,description=dosctr )
                subparser.set_defaults( ** { _EXTRA_KWD : N } )
            else:
                raise InitializationError('invalid type (%s) for sub-command "%s" of %s' % ( node.__name__, name, type(self).__name__ ) )



        word = None
        try:
            q = args[0]
            node = nodes[q]
            word = q
        except (KeyError,IndexError):
            argparse.ArgumentParser.parse_args( parser, args )

        if word is not None:
            if issubclass(node,Function):
                q = argparse.ArgumentParser.parse_args( parser, args )
                return getattr(q,_EXTRA_KWD)( q )
            elif issubclass(node,Node):
                q = argparse.ArgumentParser.parse_args( parser, [word] )
                return getattr(q,_EXTRA_KWD).digest( prog='%s %s' % (prog,word) # chaining
                                                     , args=args[1:] )
            else:
                raise TypeError


def histfile():
    "Returns file path of the hierarchical subcommand history file"
    varb = 'ARGPEXT_HISTORY'
    return os.getenv(varb)


class Unit(object):
    "Value unit for Categorical variables."
    def __init__(self,value,help=None,callable=False):
        self._value = value
        assert(isinstance(help,(str,type(None),) ))
        self._help = help
        self._callable = callable
        assert(isinstance(callable,bool))
    def evaluate(self):
        return self._value() if self._callable else self._value


class Categorical(object):
    "Categorical variable type."""
    def __init__(self,mapping=(),typeothers=None):
        L = []
        count = 0
        for q in mapping:
            count += 1
            if isinstance(q,str): 
                item = (q, Unit(value=q))
            elif isinstance(q,(list,tuple)):

                if len(q) != 2: 
                    raise InitializationError('invalid size %d for %s item number %d' % ( len(q), type(q).__name__, count ) )

                if not isinstance(q[1],Unit):
                    q = [q[0],Unit(value=q[1])]
                item = q
            else:
                raise InitializationError('invalid type (%s) for mapping item number %d.' % ( type(q).__name__, count ) )
            L += [ item ]

        self.__dict = collections.OrderedDict(L)
        self.__typeothers = typeothers

    def __str__(self):
        K = []
        for key,choice in self.__dict.items():
            K += [key]

        q = self.__typeothers
        if q is not None:
            K += ['%s()' % q.__name__ ]

        return '{%s}' % ( '|'.join(K) )

    def __call__(self,key):
        "Finds and returns value associated with the given key."
        if key in self.__dict:
            return self.__dict[key].evaluate()
        else:
            if self.__typeothers is None:
                raise KeyEvaluationError('unmatched key: "%s".' % (key) )
            else:
                return self.__typeothers(key)


class History(Function):
    "Display command line history."

    @staticmethod
    def HOOK():
        q = histfile()
        if q is not None:
            try:
                with open(q) as fhi:
                    for line in fhi:
                        print(line.rstrip())
            except:
                print('no history file found')


class Main(Node):
    "Hierarchical extension of argparse"
    SUBS = [('history', History)
            ]

if __name__ == '__main__':
    Main().digest()
