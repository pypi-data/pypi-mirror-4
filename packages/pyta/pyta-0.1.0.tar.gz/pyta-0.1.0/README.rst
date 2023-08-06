======================================
Pyta: Inner Method Dispatch for Python
======================================

Pyta = Python + Beta

Inspired by: http://www.cs.utah.edu/plt/publications/oopsla04-gff.pdf


Usage
=====

Inner dispatch is used to guarantee pre- and post-conditions without
using auxiliary methods.

Full example::

    from pyta import inner, BetaMetaclass
    
    class A(object):
        def foo(self):
            print "world!"
    
    class B(A): # Can inherit from regular classes
        __metaclass__ = BetaMetaclass
        
        def foo(self):
            inner(B, self).foo()
            super(B, self).foo()
    
    class C(B):
        def foo(self):
            print "Hello, "

Caveats
=======

Naively checks the source of the method to see if it calls <inner>.
Currently, it does <'inner(' in src>, so it will detect things like 'winner('
as well. Will be fixed in a later release.
