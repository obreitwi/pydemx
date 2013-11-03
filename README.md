PYthon DEMultipleXer
========
*(Still work in progress!)*

Whenever working on multiple computers, many files (configuration files etc.)
are largely the same except for small differences. Not all programs allow their
configuration files to have hostname- (or whatever) dependent sections.

This small script addresses that issue: You can define a single skeleton file
to use across all hosts that is compiled into a specific version upon invoking
`pydemx`.

My use case is primarily the dependence on the hostname, but the function
providing the key on which the single replacements are dependent can be
modified.


