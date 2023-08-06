cliTunes
=========

For now, this is just a command-line interface to iTunes. It's pretty
simple, but I am considering making it do a lot of more interesting
things as time goes by.

Installation
------------

To install, simply use **pip** or **easy_install**:

    easy_install clitunes

Usage
-----

Put bin/clitunes somewhere in your path. Now, you can handle playback like
this:

    clitunes play
    clitunes pause
    clitunes stop

You can also navigate files like this:

    clitunes rewind
    clitunes fast forward
    clitunes resume

or perform a lot of other useful actions:

    clitunes subscribe \"http://example.com/podcast.xml\"

Running clitunes without any options will assume that you want to use the
"playpause" command. This will play unless already playing, at which time
it will pause instead.

TODO
----

- Figure out how to be smarter about stringifying things. Passing strings to
  iTunes shouldn't require a user to escape every quote manually.

