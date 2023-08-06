.. contents::

=======
hghooks
=======

hghooks is a simple module that adds several useful hooks for use in
Mercurial hooks system.

Right now it includes hooks for:

 * pep8 checking of python files
 * pyflakes checking of python files
 * jslint checking of javascript files
 * checking for forgotten pdb statements in python files
 * Trac integration. This includes:
   - Making sure at least a ticket is mentioned in the changeset message
   - Updating the Trac ticket with the changeset


Documentation
=============

Installation
------------

hghooks is distributed as a Python egg so is quite easy to install. You just
need to type the following command::

 easy_install hghooks

And Easy Install will go to the Cheeseshop and grab the last hghooks for you.
It will also install it for you at no extra cost :-)


Usage
-----

To use one of the hooks provided by this package edit your hgrc file of
your Mercurial repository and add these lines::

 [hooks]
 pretxncommit.pep8 = python:hghooks.code.pep8hook
 pretxncommit.pyflakes = python:hghooks.code.pyflakeshook
 pretxncommit.pdb = python:hghooks.code.pdbhook
 pretxncommit.jslint = python:hghooks.code.jslinthook

You can add as many hooks as you need. From version 0.2.0 it supports the
pretxnchangegroup hook too.

How to skip the hooks
---------------------

If you need to avoid a hook for a specific changeset you can add one or
more of the following keywords to the commit message: no-pep8,
no-pyflakes and no-pdb.

On the other hand, if you want to avoid a hook in a specific file you
can add a comment somewhere in the file saying so. For example::

 # hghooks: no-pyflakes no-pdb no-jslint

in this case the pyflakes and pdb hooks will skip this file. The
"``# hghooks:``" prolog is important and you have to type it exactly
like that. Then add the skip keyworkds separated by spaces.

Skipping specific pep8 errors
-----------------------------

If you want to ignore some pep8 errors you can do so by adding a [pep8]
configuration section into your hgrc file. For example, if you want
to allow longer than 79 character lines, you would add this configuration::

 [pep8]
 ignore = E501

The format of the value of the ignore option is a space separate list of
pep8 errors or warnings. Check pep8 documentation to see these codes.

Note: this only works since pep8 0.6.0 and later versions.

Trac integration
----------------

Starting with version 0.3.0 there is some limited support for Trac integration.

Right now there are two useful hooks for those that use Trac as their project
system. The first one is a hook suitable for the pretxnchangegroup event in the
centralized repository that Trac syncs from that checks at least a ticket is
mentioned in the changeset message. The other one could be used in two ways:

 1. One is suitable for incoming event and will add a comment for every
    changeset in the ticket mentioned in the changeset message. In summary,
    one comment per commit.
 2. The other one is suitable for changegroup event. It all changesets will
    be grouped in one comment and will be added in every ticket mentioned in
    the changeset message. So for summarizing, it will register comment per
    push.

To use these hooks you must configure your repository with the Trac environment
path you want to integrate with. Write this in your .hg/hgrc repository conf::

 [trac]
 environment = /full/path/to/your/trac/environment

Now you can add both hooks in the same configuration file::

 [hooks]
 pretxnchangegroup.trac = python:hghooks.trachooks.ticket_checker
 incoming.trac = python:hghooks.trachooks.ticket_updater

or 

 [hooks]
 pretxnchangegroup.trac = python:hghooks.trachooks.ticket_checker
 changegroup.trac = python:hghooks.trachooks.ticket_updater

Right now these hooks checks for the following pattern in your changeset
messages: [action] [ticket] [number] where action is any of 'close', 'closed',
'closes', 'fix', 'fixed', 'fixes', 'addresses', 'references', 'refs', 're'
and 'see', ticket is any of 'ticket', 'issue' and 'bug' and number is the
number of the ticket with a leading # character.

In the ticket_checker hook only the presence of a ticket number and any
of these actions is checked. In the ticket_updater, additional changes
are done to the ticket depending on the action itself. And a comment
is added to the ticket with a configurable message.

If you use Trac 0.12 and have more than one repository configured in
your environment you must tell the hook, which one you want to use. To
do so add the following option in the [trac] section of the repository hgrc
configuration file::

 [trac]
 repo_name = your_repo_name_in_trac

If you don't specify this option, the repository should be the default
repository in Trac. Otherwise, the links to the changeset will not work.

You can also configure how the messages will look like in the Ticket. There
are two configuration options for that::

 [trac]
 msg_template = (At [%(changeset)s]) %(msg)s
 changeset_style = long-hex

The msg_template specifies how the text of the comments will looks like. It
has two placeholders: one for the changeset id and one for the changeset
description or message. As you can see in the above example, by putting
the changeset between brackets we automatically generate a Trac link to
that changeset in the ticket comment.

The other option, changeset_style can have one of these three values:

- number: integer with the revision number
- long-hex: full hexadecimal hash of the changeset
- short-hex: the first 12 characters of the long-hex

By default, short-hex is used as the changeset_style.

You can also add more actions if the ones supplied with hghooks are not
enough for you. The extending mechanism used to allow this feature is
based in setuptools entry points so you must be familiar with them in
order to use them. Right now there are two entry points:

- hghooks.trac.ticket_commands
- hghooks.trac.token_commands

Each of them should point to a callable that returns a dictionary where
the keys are the action names and the values are callables that receive
a ticket and can modify them if they need it.
