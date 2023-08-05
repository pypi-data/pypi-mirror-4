The ``argparse_config`` utility reads defaults for commandline args from a
config file. The cute thing is, it figures out what config options to expect
based on your ``argparse`` commandline args definition.

Let's say I'm reimplementing the Mercurial commandline client. I specify the
commandline argument processing with ``argparse``, of course::

    >>> arg_parser = ArgumentParser('hg')
    >>> arg_parser.add_argument('--repository')
    >>> sub_parsers = arg_parser.add_subparsers()
    >>>
    >>> merge_parser = sub_parsers.add_parser('merge')
    >>> merge_parser.add_argument('--tool')
    >>> merge_parser.add_argument('--force', action='store_true', default=False)
    >>>
    >>> commit_parser = sub_parsers.add_parser('commit')
    >>> commit_parser.add_argument('--user')
    >>> commit_parser.add_argument('--message')

When I go to use this client, though, I have to keep specifying my ``--user``
with every commit, and ``--tool`` with every merge. That sucks! What I want is
to have my client understand a simple config file format::

    [merge]
    tool: meld

    [commit]
    user: Tikitu de Jager <tikitu@logophile.org>

And obviously, as I add more arguments and subcommands to my client, it should
allow me to add defaults in the config file without writing more code.

This is what ``argparse_config`` gives you. To use it with the mercurial client
``arg_parser`` above::

    >>> import argparse_config
    >>> argparse_config.read_config_file(arg_parser, '/home/tikitu/.my_hg.cfg')

... and that's it. Calling ``arg_parser.parse_args()`` will parse args as usual,
but the *default* values will be taken from the config file, if they are given
there::

    >>> parsed_args = arg_parser.parse_args(['merge'])
    >>> parsed_args.tool
    'meld'

What can I put in the config file?
----------------------------------

Under the hood ``argparse_config`` uses the standard library ConfigParser_.
Arguments that aren't for a subcommand go in the section ``[default]``. The
names are munged from the commandline argument, removing leading dashes and
converting internal dashes to underscores (e.g. ``--log-level`` becomes
``log_level:``).

.. _ConfigParser: http://docs.python.org/2/library/configparser.html

Flags (i.e. commandline args that take no parameters) are turned on if present
in the config, just like the commandline::

    [default]
    verbose

is the equivalent of ``--verbose``. Either `verbose:` or `verbose` will work,
but (watch out!) `verbose: a-value` doesn't do anything different to `verbose`.

Writing a config file from some commandline arguments
-----------------------------------------------------

Included in the package is a utility to generate a config file following these
rules, from a given set of commandline arguments. That looks like this::

    >>> parsed_args = arg_parser.parse_args(['--repository', 'https://bitbucket.org/tikitu/argparse_config', 'merge'])
    >>> print argparse_config.generate_config(arg_parser, parsed_args, only_non_defaults=True)
    [default]
    repository: https://bitbucket.org/tikitu/argparse_config

    [merge]

    [commit]

Some complications make this less useful than it could be, sadly:

* If you use subcommands, you can only parse the args for one of them at a time.
* We can't tell the difference between default values written in code (which should
  not be added to the config file) and written in a previously-read-in config file
  (which should). This is why `only_non_defaults` exists.

How does it work?
-----------------

By gudgeling about in the private internals of ``argparse``. Yes, that's not
pretty.

Gotchas
-------

Any required arguments that are present in a config file will show as optional,
not required, in the ``--help`` output. (This is a bug-by-design, due to not
having any clever idea about how to do it better.) It may help to tell
yourself, "It's not required *on the commandline* because I gave it in the
config file." (I will gladly make this dodgy rationalisation disappear if I
figure out how to handle required arguments more tidily.)

Hacking
-------

It's on BitBucket_. Feel free to play. It comes with a handy ``zc.buildout``
wrapper too, overkill though that clearly is.

.. _BitBucket: http://bitbucket.org/tikitu/argparse_config

TODO
----

It's "alpha software" at present; likely to be buggy and lots of stuff ain't
there yet. Check the `issues list`_ to stay up to date. Some remaining open issues:

* How to deal with multi-value args? (The config-file library this is built on doesn't support them.)
* The "write me a config file" support is scrappy. Can we do better?

.. _issues list: http://bitbucket.org/tikitu/argparse_config/issues?status=new&status=open
