- Code repository:https://github.com/renfers/ageliaco.recipe.csvconfig
- Questions and comments to serge.renfer at gmail dot com

=========================
ageliaco.recipe.csvconfig
=========================

The idea behind this recipe is to have only one source of information for your buildout
variable settings.

When one is confronted with several deployments which are very similar, then you gather
the variable elements into a csv file (just like a flat representation of several columns).

For instance, let's say you need to generate several Plone instances and you want to gather
them in a same buildout, because you will add a supervisor and a cache with varnish, plus
a config for the nginx that runs on your server.

Your CSV file, main.csv::

    instance,port,domain,subdomain,plone,emailadmin
    albertcair,15004,albertcair.ch,base.albertcair.ch,/,albert.cair@gmail.com
    albertcair,15004,albertcair.ch,albertcair.ch,/alberto,albert.cair@gmail.com
    albertcair,15004,albertcair.ch,www.albertcair.ch,/alberto,albert.cair@gmail.com
    albertcair,15004,albertcair.ch,histoire.albertcair.ch,/bestie,albert.cair@gmail.com
    albertcair,15004,albertcair.ch,images.albertcair.ch,/images,albert.cair@gmail.com
    albertcair,15004,albertcair.ch,italiano.albertcair.ch,/italiano,albert.cair@gmail.com
    bopip,15005,bopip.ch,base.bopip.ch,/,jm.del@gmail.com
    bopip,15005,bopip.ch,bopip.ch,/bopip,jm.del@gmail.com
    bopip,15005,bopip.ch,www.bopip.ch,/bopip,jm.del@gmail.com
    bopip,15005,bopip.ch,jaun.bopip.ch,/jaun,jm.del@gmail.com
    bopip,15005,bopip.ch,java.bopip.ch,/java,jm.del@gmail.com
    bopip,15005,bopip.ch,math.bopip.ch,/math,jm.del@gmail.com
    bopip,15005,bopip.ch,ecole-en-sauvygnon.ch,/ensauvygnon,jm.del@gmail.com
    bopip,15005,bopip.ch,www.ecole-en-sauvygnon.ch,/ensauvygnon,jm.del@gmail.com

In your buildout you will be able to spread those information at different levels, 
that means on different templates.
Let's make a *templates* directory in our buildout and we put our first template

instances.cfg.in::

    [${subdomain}-parameters]
    port = ${port}
    host = 127.0.0.1
    plone = ${plone}
    name = ${instance}

and a second one

varsetting.cfg.in::

    [var-settings]
    vh-targets =
        ${subdomain}:${subdomain}-parameters
    
    instances-targets =
        ${instance}:${instance}-parameters
    
    backup-targets =
        backup-${instance}:${instance}-parameters
    
    cron-targets =
        cron-${instance}:${instance}-parameters
    
    supervisor =
        20 ${instance} ${buildout:directory}/bin/${instance} [console] true ${users:zope}
    
    eventlistener =
        ${instance}-HttpOk TICK_60 ${buildout:bin-directory}/httpok [-m ${emailadmin} -p ${instance} http://localhost:11011]


Notice that our variables have the ``${var}`` format.

In a buildout file you will have a part that has the following form:

main.cfg::

    [buildout]
    parts = main
    
    eggs = ageliaco.recipe.csvconfig
    
    
    [main]
    recipe = ageliaco.recipe.csvconfig:default
    csvfile = main.csv
    templates = templates/varsetting.cfg.in
        templates/instances.cfg.in

Running the following commands::

    ../Python-2.7/bin/python bootstrap.py -c main.cfg
    bin/buildout -c main.cfg
    
It will generate 2 files in your buildout directory, 

varsetting.cfg::

    [var-settings]
    vh-targets = 
        base.albertcair.ch:base.albertcair.ch-parameters 
        albertcair.ch:albertcair.ch-parameters 
        www.albertcair.ch:www.albertcair.ch-parameters 
        histoire.albertcair.ch:histoire.albertcair.ch-parameters 
        images.albertcair.ch:images.albertcair.ch-parameters 
        italiano.albertcair.ch:italiano.albertcair.ch-parameters 
        base.bopip.ch:base.bopip.ch-parameters 
        bopip.ch:bopip.ch-parameters 
        www.bopip.ch:www.bopip.ch-parameters 
        jaun.bopip.ch:jaun.bopip.ch-parameters 
        java.bopip.ch:java.bopip.ch-parameters 
        math.bopip.ch:math.bopip.ch-parameters 
        ecole-en-sauvygnon.ch:ecole-en-sauvygnon.ch-parameters 
        www.ecole-en-sauvygnon.ch:www.ecole-en-sauvygnon.ch-parameters
    instances-targets = 
        albertcair:albertcair-parameters 
        bopip:bopip-parameters
    backup-targets = 
        backup-albertcair:albertcair-parameters 
        backup-bopip:bopip-parameters
    cron-targets = 
        cron-albertcair:albertcair-parameters 
        cron-bopip:bopip-parameters
    supervisor = 
        20 albertcair ${buildout:directory}/bin/albertcair [console] true ${users:zope} 
        20 bopip ${buildout:directory}/bin/bopip [console] true ${users:zope}
    eventlistener = 
        albertcair-HttpOk TICK_60 ${buildout:bin-directory}/httpok [-m albert.cair@gmail.com -p albertcair http://localhost:11011] 
        bopip-HttpOk TICK_60 ${buildout:bin-directory}/httpok [-m jm.del@gmail.com -p bopip http://localhost:11011]

and 

instances.cfg::

    [base.albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /
    name = albertcair
    
    [albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /alberto
    name = albertcair
    
    [www.albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /alberto
    name = albertcair
    
    [histoire.albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /bestie
    name = albertcair
    
    [images.albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /images
    name = albertcair
    
    [italiano.albertcair.ch-parameters]
    port = 15004
    host = 127.0.0.1
    plone = /italiano
    name = albertcair
    
    [base.bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /
    name = bopip
    
    [bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /bopip
    name = bopip
    
    [www.bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /bopip
    name = bopip
    
    [jaun.bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /jaun
    name = bopip
    
    [java.bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /java
    name = bopip
    
    [math.bopip.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /math
    name = bopip
    
    [ecole-en-sauvygnon.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /ensauvygnon
    name = bopip
    
    [www.ecole-en-sauvygnon.ch-parameters]
    port = 15005
    host = 127.0.0.1
    plone = /ensauvygnon
    name = bopip
    
varsetting.cfg.in exposes one kind of variable substitution, when a variable is present in
an option value => the option value is repeated based on the number of different result we 
have in the csv file configuration, for instance the "instance" column in my csv file has 
2 different values then, based on that the "eventlistner" option expands in a 2 lines value.

instances.cfg.in exposes another kind of variable substitution, where the variable is present
in the section identifier => the section with the "subdomain" variable will epxand in as
many sections as there are different values for this variable in the csv file.

CSV as flat database :
----------------------
Let's see another example to show you that the csv file can be just a flat representation 
of a relational database.

The csv file, testmultikey.csv::

    prenom, nom, naissance, profession
    bob,wut,1961,doc
    marie,wut,1962,maitresse
    serge,ren,1960,prof
    coco,ren,1961,maitresse
    
The template, templates/contact.cfg.in::

    [contact]
    ${prenom}-${nom}-${naissance} = ${profession}
    
    [famille-${nom}]
    ${prenom}-naissance = ${naissance}
    ${prenom}-profession = ${profession}
    
    [annee-de-naissance-${naissance}]
    ${prenom}-${nom} = ${profession}
    
    [${profession}]
    nom = ${prenom}-${nom}-${naissance}

and now the buildout, buildout.cfg::

    [buildout]
    
    parts = main
    
    develop = src/ageliaco.recipe.csvconfig
    eggs =
        ageliaco.recipe.csvconfig
        
    [main]
    recipe = ageliaco.recipe.csvconfig
    templates = templates/contact.cfg.in
    csvfile = testmultikey.csv

and the result of `bin/buildout`, contact.cfg::

    [contact]
    bob-wut-1961 = doc
    coco-ren-1961 = maitresse
    marie-wut-1962 = maitresse
    serge-ren-1960 = prof
    
    [famille-ren]
    coco-naissance = 1961
    serge-naissance = 1960
    coco-profession = maitresse
    serge-profession = prof
    
    [famille-wut]
    bob-naissance = 1961
    marie-naissance = 1962
    bob-profession = doc
    marie-profession = maitresse
    
    [annee-de-naissance-1961]
    bob-wut = doc
    coco-ren = maitresse
    
    [annee-de-naissance-1962]
    marie-wut = maitresse
    
    [annee-de-naissance-1960]
    serge-ren = prof
    
    [maitresse]
    nom = marie-wut-1962
            coco-ren-1961
    
    [doc]
    nom = bob-wut-1961
    
    [prof]
    nom = serge-ren-1960

