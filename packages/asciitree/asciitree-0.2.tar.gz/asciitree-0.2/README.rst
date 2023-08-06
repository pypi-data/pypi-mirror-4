ASCII Trees
===========

Occasionally, you want things to look slightly pretty in the terminal. If trees are involved, give asciitree a shot!

Sample output
-------------

Here's a code sample::

    class Node(object):
        def __init__(self, name, children):
            self.name = name
            self.children = children

        def __str__(self):
            return self.name

    root = Node('root', [
        Node('sub1', []),
        Node('sub2', [
            Node('sub2sub1', [])
        ]),
        Node('sub3', [
            Node('sub3sub1', [
                Node('sub3sub1sub1', [])
            ]),
            Node('sub3sub2', [])
        ])
    ])

    print draw_tree(root)


and its output::

     root
       +--sub1
       +--sub2
       |  +--sub2sub1
       +--sub3
          +--sub3sub1
          |  +--sub3sub1sub1
          +--sub3sub2


API
---

The module consists of a single public function, with the following signature:

``draw_tree(node, child_iter, text_str)``

where ``node`` is the root of the tree to be drawn, ``child_iter`` is a
function that when called with a node, returns an iterable over all its
children and ``text_str`` turns a node into the text to be displayed in the
tree.

The default implementations of these two arguments retrieve the children by
accessing ``node.children`` and simply use ``str(node)`` to convert a node to a
string.

The resulting tree is drawn into a buffer and returned as a string.
