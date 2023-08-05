********************************
zookeeper-deploy buildout script
********************************

Usage:

Create a part in your rpm buildout::

  [zookeeper-deploy]
  recipe = zc.recipe.egg
  eggs = zc.zookeeper_deploy_buildout
  arguments = 'APP', 'RECIPE'

where

APP
   the name of your application and the name of the directory in
   ``/etc`` where deployments will be recorded

RECIPE
   the name of the meta-recipe to use

In development mode, you can include initlization logic to run the
recipe in development mode:

  [zookeeper-deploy]
  recipe = zc.recipe.egg
  eggs = zc.zookeeper_deploy_buildout
  arguments = 'APP', 'RECIPE'
  initialization = zc.zookeeper_deploy_buildout.development_mode = True


Changes
*******

0.2.0 (2012-09-25)
==================

- Allow the application name (APP) to be blank or None, in which case
  it's determined from the script name.

- Added a -r option to specify a recipe entry point to the recipe
  supplied to main.

0.1.0 (2012-05-31)
==================

Initial release
