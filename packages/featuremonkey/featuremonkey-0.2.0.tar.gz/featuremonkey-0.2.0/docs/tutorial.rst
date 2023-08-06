**************************
featuremonkey Tutorial
**************************

This tutorial is a quick introduction to building SPLs using featuremonkey.
See the reference for in depth discussion.

Example Product Line
========================

To get started, we use the well-known Greeter example.
We will build a product line of greeters according to the following feature model:

.. graphviz::

    digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10, shape=box];
        edge [arrowhead=none];
        
        "TodoMonkey" -> "base" [arrowhead=dot];
        "TodoMonkey" -> "description" [arrowhead=odot];
        "TodoMonkey" -> "filter" [arrowhead=odot];
        "filter" -> "search" [arrowhead=odot];
    }



.. graphviz::

    digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10, shape=box];
        edge [arrowhead=none];
        
        "greeter" -> "base" [arrowhead=dot];
        "greeter" -> "monkey" [arrowhead=odot];
        "greeter" -> "loud" [arrowhead=odot];
        "greeter" -> "uncertain" [arrowhead=odot];
    }


The feature model diagram translates roughly to:
A valid greeter product needs to contain the mandatory ``base`` feature.
Features ``monkey``, ``loud``, and ``uncertain`` are optional(and can also be combined).

Soon, we will be able to compose a basic greeter(``base``), a greeting monkey(``base`` + ``monkey``),
a loud greeter(``base`` + ``loud``), and even a loud and uncertain greeting monkey by selecting all the features.


Base feature and FST
====================

Now, let's look at the code. The ``base`` feature:

.. raw:: html

    <table class="fmod"><tr><td width="50%">


::

    #base.py
    def get_greeting():
        return 'Hello'
    
    def greet():
        print get_greeting()


.. raw:: html

    </td><td width="50%">


.. graphviz::

   digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10];
        edge [arrowhead=none];
        "base:module" -> "get_greeting:function";
        "base:module" -> "greet:function";
   }


.. raw:: html

    </td></tr></table>


``base`` defines two functions. On the right, the corresponding FST(feature structure tree) is shown.
As you can see, there is nothing special about the base module. Think of its FST as the namespace of the ``base`` module.

Superimposing FSTs
==================


Now, we want to tweak the base program a little, because a monkey does not say "Hello".
To change the message, we specify a different kind of FST that we can place on top of the base module.
Let's have a look at feature ``monkey``:

.. raw:: html

    <table class="fmod"><tr><td width="50%">


::

    #monkey.py
    def refine_get_greeting(original):
        
        def get_greeting():
            return 'Uga Aga'
    
        return get_greeting


.. raw:: html

    </td><td width="50%">


.. graphviz::

   digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10];
        edge [arrowhead=none];
        n1[label="get_greeting:function2",style=filled,fillcolor=yellow];
        "monkey:module" -> n1;
   }


.. raw:: html

    </td></tr></table>


Obviously, the FST on the right does not represent the namespace of the ``monkey`` module.
FSTs need to be specified in another format to place them on top of other FSTs.
We will refer to these FSTs as *superimposing FSTs* from now on.

The ``monkey`` module will serve as the root node of the FST.
To compose FSTs, featuremonkey inspects the namespace of the superimposing FST and looks for names starting with ``refine_`` (and others that are described later on). We will refer to these names as refinements.
Refinement functions accept one parameter called ``original`` - a reference to the original implementation that is to be refined. They need to return the refined value for the name.

By defining a ``refine_get_greeting`` function, we tell featuremonkey that we want to refine the existing name
``get_greeting``. Then we define an inner function ``get_greeting`` and return it.
This tells featuremonkey that this is the refined implementation for ``get_greeting``.
In the diagram of the FST, ``get_greeting`` is highlighted in orange to signify that the node represents a refinement.

Product Launchers
==================


Now, before creating the other features, let us look at how we can create the base and the monkey greeter.
Therefore, we create the following two launchers::

    #launch_base.py
    if __name__ == '__main__':
        import base
        base.greet()


When running ``python launch_base.py`` the product containing only the base feature is run.
To run the product also containing the monkey feature, we need to tweak the launcher a little::

    #launch_monkey.py
    if __name__ == '__main__':
        import base
        import monkey
        featuremonkey.compose(monkey, base)
        base.greet()

Here, we also import the monkey module. Then we call ``featuremonkey.compose`` to superimpose the the monkey FST on the base FST. Then, as before, we call ``base.greet()``. This time however, we get the modified message, as featuremonkey has
patched the base module to use the implementation of ``get_greeting`` given in the monkey feature.

Using ``original``
===================


Great, now that we know how the features are actually composed, let's create the remaining two features starting with feature ``loud``:

.. raw:: html

    <table class="fmod"><tr><td width="50%">


::

    #loud.py
    def refine_get_greeting(original):
        
        def get_greeting():
            return original().upper()
    
        return get_greeting


.. raw:: html

    </td><td width="50%">


.. graphviz::

   digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10];
        edge [arrowhead=none];
        n1[label="get_greeting:function2",style=filled,fillcolor=yellow];
        
        "loud:module" -> n1;
   }


.. raw:: html

    </td></tr></table>


Again, we create a superimposable FST, that specifies a refinement for ``get_greeting``.
But here, we make use of the original implementation (and simply make it louder by uppercasing the greeting).
A launcher for a loud greeter would be::

    #launch_loud.py
    if __name__ == '__main__':
        import base
        import loud
        featuremonkey.compose(loud, base)
        base.greet()


And a loud monkey greeter::

    #launch_loud_monkey.py
    if __name__ == '__main__':
        import base
        import monkey
        import loud
        featuremonkey.compose(loud, monkey, base)
        base.greet()



Composition order
=================

Please note, that the order the features are passed to compose is relevant:
The base feature must always be the last argument. Superimposable FSTs are superimposed step by step **from right to left** (the superimposition operation is defined as such in literature).

Here, this means that ``monkey`` is first superimposed on ``base``. Then, ``loud`` is superimposed on the result.
Therefore, when running the launcher, we get the monkey greeting in uppercase.

The composed FST looks rougly like the following. The feature that introduced a respective node is given in square brackets.

.. graphviz::

    digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10];
        edge [arrowhead=none];
        
        "base:module" -> "get_greeting:function\n[loud]";
        "base:module" -> "greet:function\n[base]";
        "get_greeting:function\n[loud]" -> "get_greeting:function\n[monkey]" [style=dotted, arrowhead=empty, label=original, fontsize=8];
        "get_greeting:function\n[monkey]" -> "get_greeting:function\n[base]" [style=dotted, arrowhead=empty, label=original, fontsize=8];
        
    }


If we would change the composition order to
``(monkey, loud, base)`` running it would simply yield the monkey greeting (as the implementation of ``get_greeting`` in ``monkey`` hides the implementation in ``loud`` and ``base`` by not making a call to ``original``).


Specifying Superimposing FSTs
==============================

As we have seen before, we can specify superimposing FSTs by creating a python module that is used as root node of the FST. Functions defined in this module starting with ``refine_`` are special and are used to create child nodes in the FST.
In fact, featuremonkey also supports a more compact method to declare FSTs:

.. raw:: html

    <table class="fmod"><tr><td width="50%">


::

    #launch_uncertain.py
    class Uncertain(object):
        def refine_get_greeting(self, original):
            
            def get_greeting():
                return original() + '?'
            
            return get_greeting
    
    if __name__ == '__main__':
        import base
        featuremonkey.compose(Uncertain(), base)
        base.greet()


.. raw:: html

    </td><td width="50%">


.. graphviz::

   digraph foo {
        graph [bgcolor="#F8F8F8"];
        node [fontsize=10];
        edge [arrowhead=none];
        n1[label="get_greeting:function",style=filled,fillcolor=yellow];
        "uncertain:module" -> n1;
   }


.. raw:: html

    </td></tr></table>


As you can see, we can also specify FSTs using classes instead of modules. Please note that you need to pass an instance to ``featuremonkey.compose``, not the class itself.

Superimposing FSTs can be superimposed on packages, modules, classes and even on individual instances - in the current example we superimposed on a module.

Introductions and Higher Trees
==============================

Until now, we have used featuremonkey to refine an existing function in module ``base``.
Other 
