
execution locals: killing global state (including thread locals)
===================================================================

This module provides execution locals aka "xlocal" objects which implement
a more restricted variant of "thread locals".  An execution local allows to
manage attributes on a per-execution basis in a manner similar to how real
locals work:

- Invoked functions cannot change the binding for the invoking function
- existence of a binding is local to a code block (and everything it calls)

Attribute bindings for an xlocal objects will not leak outside a
context-managed code block and they will not leak to other threads of
greenlets.  By contrast, both process-globals and so called "thread
locals" do not implement the above properties.

Let's look at a basic example::

    # content of example.py

    from xlocal import xlocal

    xcurrent = xlocal()

    def output():
        print "hello world", xcurrent.x

    if __name__ == "__main__":
        with xcurrent(x=1):
            output()

If we execute this module, the ``output()`` function will see 
a ``xcurrent.x==1`` binding::

    $ python example.py
    hello world 1

Here is what happens in detail: ``xcurrent(x=1)`` returns a context manager which 
sets/resets the ``x`` attribute on the ``xcurrent`` object.  While remaining
in the same thread/greenlet, all code triggered by the with-body (in this case
just the ``output()`` function) can access ``xcurrent.x``.  Outside the with-
body ``xcurrent.x`` would raise an AttributeError.  It is also not allowed
to directly set ``xcurrent`` attributes; you always have to explicitely mark their
life-cycle with a with-statement.  This means that invoked code:

- cannot rebind xlocal state of its invoking functions (no side effects, yay!)
- xlocal state does not leak outside the with-context (lifecylcle control)

Another module may now reuse the example code::

    # content of example_call.py
    import example
    
    with example.xcurrent(x=3):
        example.output()

which when running ...::

    $ python example_call.py
    hello world 3

will cause the ``example.output()`` function to print the ``xcurrent.x`` binding
as defined at the invoking ``with xcurrent(x=42)`` statement.

Other threads or greenlets will never see this ``xcurrent.x`` binding; they may even 
set and read their own distincit ``xcurrent.x`` object.  This means that all 
threads/greenlets can concurrently call into a function which will always
see the execution specific ``x`` attribute.

Usage in frameworks and libraries invoking "handlers"
-----------------------------------------------------------

When invoking plugin code or handler code to perform work, you may not
want to pass around all state that might ever be needed.  Instead of using
a global or thread local you can safely pass around such state in 
execution locals. Here is a pseudo example::

    xcurrent = xlocal.new()

    def with_xlocal(func, **kwargs):
        with xcurrent(**kwargs):
            func()

    def handle_request(request):
        func = gethandler(request)  # some user code
        spawn(with_xlocal(func, request=request))

``handle_request`` will run a user-provided handler function in a newly
spawned execution unit (for example spawn might map to
``threading.Thread(...).start()`` or to ``gevent.spawn(...)``).  The
generic ``with_xlocal`` helper wraps the execution of the handler
function so that it will see a ``xcurrent.request`` binding.  Multiple
spawns may execute concurrently and ``xcurrent.request`` will
carry the execution-specific request object in each of them.


Issues worth noting
---------------------------------------

If a method memorizes an attribute of an execution local, for
example the above ``xcurrent.request``, then it will keep a reference to
the exact request object, not the per-execution one.  If you want to
keep a per-execution local, you can do it this way for example::

    Class Renderer:
        @property
        def request(self):
            return xcurrent.request

this means that Renderer instances will have an execution-local
``self.request`` object even if the life-cycle of the instance crosses
execution units.

Another issue is that if you spawn new execution units, they will not 
implicitely inherit execution locals.  Instead you have to wrap
your spawning function to explicitely set execution locals, similar to
what we did in the above "invoking handlers" section.

Copyright / inspiration
-------------------------------------

This code is based on discussions with Armin Ronacher and others
in response to a `tweet of mine <https://twitter.com/hpk42/status/268012251888353280>`_. It extracts and refines some ideas found in Armin's "werzeug.local" module
and friends.

:copyright: (c) 2012 by Holger Krekel, partially Armin Ronacher
:license: BSD, see LICENSE for more details.
