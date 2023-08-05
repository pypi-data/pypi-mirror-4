Supported options
=================

The recipe supports the following options:

.. Note to recipe author!
   ----------------------
   For each option the recipe uses you should include a description
   about the purpose of the option, the format and semantics of the
   values it accepts, whether it is mandatory or optional and what the
   default value is if it is omitted.

csvfile
    this is a path (relative or absolute) to csv file that will be used by the recipe

templates
    one (or more) path to a template file => by default, it is expected a name with ".in" 
    suffix and a file with the same name without the suffix ".in" will be generate in the
    buildout directory. If you want to use another suffix or naming convention you will have
    to use an alternative format with a ":" to separate the template path to the target path,
    
for instance::

    templates = templates/instances.cfg.in
    
that will generate a ./instances.cfg file (in the buildout directory) or

    templates = templates/init-cache.cfg:production/cache.cfg
    
that will generate a production/cache.cfg file
     



