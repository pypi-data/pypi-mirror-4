c2c.recipe.facts
================

Collect all puppet facter facts

Example of use::

    [buildout]
    ...

    [facts]
    recipe = c2c.recipe.facts

    [echo]
    recipe = missingbits:echo
    echo =
        The hostname is ${facts:hostname}
        The operating system family is ${facts:osfamily}
        The operating system is ${facts:operatingsystem}
        The distribution code name is ${facts:lsbdistcodename}
