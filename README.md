# PYthon DEMultipleXer
*(This readme is still a stub!)*

Whenever working on multiple computers, many files (configuration files etc.)
are largely the same except for small differences. Not all programs allow their
configuration files to have hostname- (or whatever) dependent sections.

This small script addresses that issue: You can define a single `.pydemx` file
to use across all hosts that is compiled into a specific version upon invoking
`pydemx`.

My use case is primarily the dependence on the hostname, but the function
providing the key on which the single replacements are dependent can be
modified (it could also be the time of day etc).

## Basic functionality

The core concept revolves around the notion of *replacement*-objects which are
used as placeholder for the varying content in the `.pydemx` file. They are
basically dictionaries storing several `key -> value_string` pairs. Furthermore
there is a *key-function* which -- when pydemx is run -- returns a specific
`key` (e.g. the hostname of the current computer).

The `.pydemx` file is then parsed and each *replacement* replaced by its
corresponding `value_string` that corresponds to the `key`.

## `.pydemx` file syntax

(Please see the [example](example/simple.skel) along with the description here.)

### Magic line

The first line (apart from a possible shebang) in every `.pydemx` file defines
the *magic line* that is used to identify special *blocks* of python code in the
`.pydemx` file that can be used to define replacments etc.

### Prefix

The second line in every `.pydemx` file should consist of the *magic line*
defined on the first line plus a special *prefix* that usually is the comment
string for the language the `.pydemx` file is written for (`# ` for python, `-- `
for haskell etc) so that synatx parser do not get confused by the added python
code. In *code blocks* (see below) the prefix is deleted from each line before
the python code is interpreted.
If no *prefix* is desired, the second line can be omitted.

### Special blocks

Every two *magic line*s define a *block*: There are *code block*s and
*replacement block*s. The very first *code block* is the *configuration block*.

#### Code block

Code blocks are plain python code interpreted when the file is read. If *prefix*
is defined it is stripped from the lines within the block. Then the lines are
interpreted as regular python code. There is an `R` object defined which can be
used to specify replacements.

```python
R(name, default=None)[possible_key] = corresponding_string
```

where `name` is the name of the replacement and `default` corresponds to
its default value in case there is no specific value defined for the key
returned by the *key-function*. Whenever R is called with a specific `name`
it returns the same dictionary-like object that can then have several
`possible_key/corresponding_string` pairs.

#### Configuration block

The first *code block* encountered in the `.pydemx` file is called the
*configuration block*. Along with the `R` object there is a `cfg` dictionary as
well that can be used to overwrite/define certain configuration options. The
most commonly used are `filename`/`folder` that define where the generated file
should be placed.

Everything can be customized, for instance how replacements appear in the
`.pydemx` file, what the default designator is and how replacement block
designates its key value.

(TODO: Go into details here. --obreitwi, 26-12-13 12:21:28)

#### Replacement block

A replacement block is basically an easier way to perform multiline
replacements. They are defined by the regular *magic line* followed by the name.
A specific value is indicated by the designator (default: `name @ key-value`).

Several replacements blocks can follow each other without the need of a
terminating *magic line* after each.

