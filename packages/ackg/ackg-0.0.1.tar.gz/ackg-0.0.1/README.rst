ackg
====

With `ackg` for Linux you can search folders of your harddrive for
source files containing a given pattern, similar to grep.

As `ackg` does not search all files, but only files that are supposed
to contain code, it can be faster than grep.

It attempts to be a more convenient method of calling GNU find, xargs,
(or parallel) and grep, by providing better default options and
command line structure.

`ackg` was inspired by `ack-grep <http://betterthangrep.com/>`_, which
users on other operating systems may prefer.

Usage
=====

ackg is a command line tool.

usage: ackg [OPTIONS] PATTERN [PATH*]

* OPTIONS allows to change the behavior
* PATTERN defines what you search for
* PATH is a list of locations to search, defaults to current folder

See `ackg --help` for more details

Download
========

Source code and issue tracker at:
http://github.com/tkruse/ackg


Why ackg?
=========

`ackg` attempt to make life easier for developers new to the command
line. `grep` is a useful tool to search files, but it does not have
convenient default behavior with respect to files you usually do not
want to search in as a developer, such a binary files, temporary
files, or files in version control repository folders like .svn or
.git.

`ack-grep` does whitelisted code-search, but reinvents the wheel by
reimplementing search, and `ack-grep` is written in Perl, which is not
everyone's cup of tea. The only advantage ack-grep has is portability
to other operating systems.

`ackg` is usually faster than `ack-grep` because it relies on
optimized code written in C to do the heavy lifting, and because
it offers to parallelize jobs, making full use of multiple CPUs.

`ackg` is free and open, you can read the code and contribute.

How does it work?
=================

`ackg` creates a command that is run on the command line, and you can
see what it would run by using the --dry command.
