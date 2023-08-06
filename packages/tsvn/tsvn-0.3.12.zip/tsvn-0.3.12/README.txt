README.TXT
~~~~~~~~~~

tsvn - a commandline interface to TortoiseSVN
~~~~------------------------------~-------~~~

Commandline and graphical clients to SCM systems have specific strengths.
Terminal programs are often executed quicker, and their output can be
redirected for further processing; graphical clients are often more convenient
when it comes e.g. to browsing the logs.  Thus, many developers will want to
use both.  Unfortunately, their commandline interfaces are totally different.

This package provides a single tool called "tsvn" which eases the commandline
usage of TortoiseSVN by mimicking the svn commandline syntax and semantics as
closely as possible.

Of course, there is

  tsvn help                (like "svn help")

to give an overview of the implemented commands, and

  tsvn help <command>      (like "svn help <command>")

to tell about the usage of <command>.

The task is non-trivial, because the usage of the graphical and the commandline
client is quite different, e.g. when it comes to Subversion properties
(svn:eol-style and the like).

While the interface is still incomplete, it is already useful:  Use ...

  tsvn log                  to get the history for the current working
                            directory
  tsvn ci                   to see your current changes to the working
                            directory, select and deselect entries, view
                            diffences by right-clicking files,
                            and finally commit

Some commands were added (which are not present in svn), e.g. ...

  tsvn explore              to explore the repository, starting at the URL of
                            the current working copy
  tsvn ce                   to call the conflicts editor.

(and more.)


Things to do
~~~~~~~~~~~~

- TortoiseSVN expects message files or file lists in UTF-16 encoding which is
  rather uncommon for normal file editor usage.  For -F/--file arguments, an
  appropriate temporary file will need to be created.

- ...


Unsolved issues
---------------

Often the commandline is used on a virtual Linux machine, while TortoiseSVN is
a Windows(tm) explorer extension.  To handle this situation, some server
infrastructure would be needed to hand over the tsvn command to a server
process, running on the Windows host, which in turn executes TortoiseSVN.
The given tool will work only for situations where commandline shell and
TortoiseSVN run on the same operating system instance.

A Linux (KDE, GNOME...) shell extension will very likely use completely
different commandline arguments; for Linux usage, a "gsvn" (or similar)
executable might be useful (like gvim/vim).

