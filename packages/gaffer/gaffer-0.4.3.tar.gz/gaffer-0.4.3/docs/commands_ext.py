import os
from gaffer.node.commands import get_commands

_HEADER = """\
.. _cli:

Gafferctl
=========

*gafferctl* can be used to run any command listed below. For
example, you can get a list of all processes templates::

    $ gafferctl processes


*gafferctl* is an HTTP client able to connect to a UNIX pipe or a tcp
connection and connect to a gaffer node. It is using the httpclient
module to do it.

You can create your own client either by using the client API provided
in the httpclient module or by reading the doc here and passing your own
message to the gaffer node. All messages are encoded in JSON.

.. image:: _static/gaffer_watch.png

Usage
+++++

::

    $ gafferctl help
    usage: gafferctl [--version] [--connect=<endpoint>]
                     [--certfile] [--keyfile]
                     [--help]
                     <command> [<args>]

    Commands:
        add           	Increment the number of OS processes
        add_process   	Add a process to monitor
        del_process   	Get a process description
        get_process   	Fetch a process template
        help          	Get help on a command
        kill          	Send a signal to a process
        load_process  	Load a process from a file
        numprocesses  	Number of processes that should be launched
        pids          	Get launched process ids for a process template
        processes     	Add a process to monitor
        running       	Number of running processes for this process description
        start         	Start a process
        status        	Return the status of a process
        stop          	Stop a process
        sub           	Decrement the number of OS processes
        update_process	Update a process description


"""


def generate_commands(app):
    path = os.path.join(app.srcdir, "commands")
    ext = app.config['source_suffix']
    if not os.path.exists(path):
        os.makedirs(path)

    tocname = os.path.join(app.srcdir, "gafferctl%s" % ext)

    with open(tocname, "w") as toc:
        toc.write(_HEADER)
        toc.write("gafferctl commands\n")
        toc.write("-------------------\n\n")

        commands = get_commands()
        for name, cmd in commands.items():
            toc.write("- **%s**: :doc:`commands/%s`\n" % (name, name))

            # write the command file
            refline = ".. _%s:" % name
            fname = os.path.join(path, "%s%s" % (name, ext))
            with open(fname, "w") as f:
                f.write("\n".join([refline, "\n", cmd.desc, ""]))

        toc.write("\n")
        toc.write(".. toctree::\n")
        toc.write("   :hidden:\n")
        toc.write("   :glob:\n\n")
        toc.write("   commands/*\n")

def setup(app):
    app.connect('builder-inited', generate_commands)
