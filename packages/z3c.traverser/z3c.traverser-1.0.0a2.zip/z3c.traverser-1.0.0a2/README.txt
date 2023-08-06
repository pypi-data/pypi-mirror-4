This package provides the pluggable traverser mechanism allowing developers
to add new traversers to an object without altering the original traversal
implementation.

In addition to the pluggable traversers, this package contains two more
subpackages:

 * viewlet - provides a way to traverse to viewlets using namespaces
 
 * stackinfo - provides a way to consume parts of url and store them
   as attributes of the "consumer" object. Useful for urls like:
   /blog/2009/02/02/hello-world
