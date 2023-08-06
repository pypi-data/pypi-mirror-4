README.TXT
~~~~~~~~~~

THeBoPS-envtools - Tools for environment variables
~~~~~~~~~~~~~~~~---~~~~~-----~~~------------------

Contains some tools related to environment variables:

py-env
  Tell about environment variables which are used by the Python interpreter or
  certain Python software


"Coming soon"
-------------

The following tools need some work because it won't work (cross-platform) to
add their current form as scripts to the setup; they will follow soon:

scanpath
  Find programs in a PATH, similar to the "which" command (which is not present
  on Windows(tm) systems).

listpath
  List the PATH (or a PATH-like variable)

modpath
  inserts, deletes, checks ... entries of a PATH-like variable.
  Since a Python program is run in a new process, it can't change the value of
  an environment variable directly; thus it must be wrapped using a shell
  function (*X) or a batch script (Windows).

