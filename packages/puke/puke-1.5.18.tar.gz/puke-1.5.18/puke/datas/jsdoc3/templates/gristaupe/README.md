Overview
========

GrisTaupe is an extremely simple template that outputs json, to be consumed by a javascript webapp (or anything else that can read json obviously...).

There is very little assumption on the format of the data itself - it does barely clean-up jsdoc methods and meta information, and organizes things in a tree (just like haruki).

The purpose is to delegate most useful processing / presentation to something entirely outside of jsdoc.

And, ha, it does only output to console.

Usage
=====

    ./jsdoc myscript.js -t templates/gristaupe -d console

The results of this command will appear in `stdout` and can be piped into other tools for further processing.

More
=====

This is meant primarily to fit WebItUp internal needs, but if you think this is useful / interesting, then good for you! Fork it / patch it / do whatever you want with it.
If you are interested in GrisTaupe, then good for you!
