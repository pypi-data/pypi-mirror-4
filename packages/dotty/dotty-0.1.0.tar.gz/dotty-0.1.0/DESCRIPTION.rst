Description
-----------

dotty is a simple tool to aid with configuration file
management.

dotty lets you keep all your personal dotfiles for
all your computers in a single directory (optionally, but
highly-advantageously, under version control). You can
define different configurations for your different
computers using "roles", which are specific sets of
dotfiles. Roles support inheritance.

Running dotty takes a single required argument; the name of the role you want
to use. Dotty will them symlink the dotfiles for that role to their proper
places on your machine.

This means that setting up a new computer just means cloning
your dotfiles repository to your home directory and running
dotty, which will take care of the rest for you.
