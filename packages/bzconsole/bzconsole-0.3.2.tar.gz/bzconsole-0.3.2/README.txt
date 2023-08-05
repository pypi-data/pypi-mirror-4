bzconsole
=========

bzconsole is a simple python API to bugzilla's bzapi.  
Currently, it only has a few functions, including getting the
configuration, listing the products and components, and filing a new
bug.  I mostly introduced it to make filing bugs from the command line
simple. I'll probably include more features going forward as I need
them, but if anyone else is interested I'm happy to take feature
requests.  

Usage
-----

The console entry point is ``bz``.  Invoking without options gives you
the usage and help.  The general pattern is 
``bz [options] <command> [command-options]`` . Using ``bz help <command>`` 
displays the help for the command.

You can have a ~/.bz dotfile to contain your username and password in.

Feel free to contact me with any questions!

jhammel@mozilla.com
