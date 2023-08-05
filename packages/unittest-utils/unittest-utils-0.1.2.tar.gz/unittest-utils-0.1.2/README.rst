unittest2-utils
===============

A custom module that adds some functionality to unitest (or unittest2)
python module.

It adds the following:

* It runs the test based on the line of code where the method was defined.
  Unittest order this using the method name
* It prints some color output when there is a string difference when
  using assertEqual or assertEquals

How to use it
--------------

It behaves the same as unittest2. Some from the command line to run
unittest2 use you have the following options:

    unittest-utils discover
    unittest-utils mymodule.test.test_module
    ....

