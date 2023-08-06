hoard (CLI)
===========
This utility allows you to pull variables for a project from your [treasure] `hoard
<http://github.com/ghickman/hoard>`_.


Installation
------------
Use your favourite python package installer::

    pip install hoard-cli


Configuration
-------------
Set your hoard url and default environment in ``~/.hoardrc``::

    [hoard]
    url=<some_url>
    env=dev


Set your project name in your project's ``.hoard`` (ideally in your project's top level directory)::

    [hoard]
    project=<project_name>


Usage
-----
List environments for a project, with overrides for project and env::

    hoard get [--project] [--env]


Set one or more environment variables, with overrides for project and env::

    hoard set [--project] [--env] KEY=value [KEY=value,...]


Delete one or more environment variables, with overrides for project and env::

    hoard rm [--project] [--env] KEY [KEY,...]


Project specific commands, e.g. show the current project, list envs for current project, list all projects::

    hoard project [project] [--envs] [--all]


Environment specific commands, e.g. show the current env, list all envs::

    hoard env [--all]


Get your auth token from the server backend::

    hoard login


Clear your local auth token::

    hoard logout

