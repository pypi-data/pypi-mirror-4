===========
dotty 0.1.0
===========

By Thomas Scrace <tom@scrace.org>

-----------
Description
-----------

dotty is a simple tool to aid with configuration file
management.

dotty lets you keep all your personal dotfiles for all your
computers in a single directory (optionally, but
highly-advantageously, under version control). You can define
different configurations for your different computers using
"roles", which are specific sets of dotfiles. Roles support
inheritance.

Running dotty takes a single required argument; the name of the
role you want to use. Dotty will them symlink the dotfiles for
that role to their proper places on your machine.

This means that setting up a new computer just means cloning
your dotfiles repository to your home directory and running
dotty, which will take care of the rest for you.

------------
Installation
------------

From the development repository
===============================

Clone the repo::

    $ git clone https://github.com/thomas-scrace/dotty.git
    $ cd dotty

Build the distribution and install::

    $ python setup.py build
    $ python setup.py install

From the pre-build distro
=========================

Download the tarball::

    $ curl -O http://files.scrace.org/software/dotty-0.1.0.tar.gz

Extract it and change into the dotty directory::

    $ tar -xzvf dotty-1.0.1.tar.gz
    $ cd dotty-1.0.1

Install::

    $ python setup.py install

------
Source
------

The source code for dotty is available at:

https://github.com/thomas-scrace/dotty

-----
Usage
-----

Dotty has the concept of "roles", which each describe a specific
set of software configuration files. Roles can inherit files
from other roles. For example, you might have one role for home
and one for work. Likely there will be a lot of overlap between
configurations.

In some cases, for example, it might just be that your
.gitconfig file needs a different author email address at home
than at work, and that all your other configuration files should
be shared between home and work. In such a case you can define
a base role where most of your configuration lives, and child
roles that contain only the differing dotfiles. This enables
code reuse.

---------------
Creating a Role
---------------

Make a subdirectory within your dotfiles directory. The name of
this directory is the name of the role. Put the dotfiles for
this role inside the role directory.

----------------------------------
Updating a workstation with a role
----------------------------------

Now that you have created a role, you can update a particular
computer with the role's configuration files. To do this just
type dotty followed by the name of the role. For example, to
update using a role called "home", just type::

    $ dotty home

By default this will cause every file (both directories and
regular files) in your home role's directory to be symlinked
from your home directory.

For example, given the following role::

    - ~/
      - dotfiles/
        - home/
          - vimrc
          - gitconfig
          - gitignore

Running::

    $ dotty home

Will result in the following additional files appearing in your
home directory::

    .vimrc -> dotfiles/home/vimrc
    .gitconfig -> dotfiles/home/gitconfig
    .gitignore -> dotfiles/home/gitignore

My preference is to keep undotted files in role directories. If
you do so, dotty will automatically prepend the dot for you.

-------------------------------------
Specifying non-default link locations
-------------------------------------

Although by default dotty will link to your dotfiles from your
home directory, you can override this by specifying a different
location in role.conf.

For example, if you want to link your gitconfig dotfile not from
your home directory, but from /etc you can create a role.conf
file within your role directory and add the following line::

    gitconfig /etc/gitconfig

This tells dotty to link the gitconfig file from /etc/gitconfig.
Note that because you have explicitly specified the link name no
dot will be prepended.

----------
Inheriting
----------

To inherit from another role, add the following line to the
child role's role.conf file::

    inherit <name_of_parent_role>

Consider the following dotfiles directory structure::

    - ~/
      - dotfiles/
        - home/
          - vimrc
          - gitconfig
          - gitignore
        - work/
          - role.conf
          - gitconfig

If ~/dotfiles/work/role.conf contains::

    inherit home

The work role will inherit home's vimrc and gitignore, but will
ignore home's gitconfig in favour of its own. Inheritance chains
can be arbitrarily long. Files lower down the chain will
override files of the same name from higher up the chain. Link
locations specified in role.conf files will be inherited and can
be overridden by child roles.

-------------------------------------------------
Specifying the location of the dotfiles directory
-------------------------------------------------

By default dotty will look for roles in ~/dotfiles. You can
specify an different location in three ways, in order of
decreasing priority:

1. By passing a --srcdir (or -c) argument when calling dotty::

    dotty <role_name> --srcdir <path_to_dotfiles>

2. By adding a line to ~/.dottyrc::

    srcdir <path_to_srcdir>

3. By adding a similar line to /etc/dottyrc
