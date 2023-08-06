=============================
 NARC
=============================

Narc is a a program that's primary function is to be an auto-responder to Slick
(http://code.google.com/p/slickqa) events.

Although it's first usage will be for sending emails (or narc'ing on slick),
narc is built to be pluggable and respond to any events in slick.

Usage is simple, a command line script is included in the program, simply run
it.  By default it looks for a configuration file in /etc/narc.ini, however
you can customize what configuration file it uses by using the command line
switch of -c or --config and specify a different configuration file.

