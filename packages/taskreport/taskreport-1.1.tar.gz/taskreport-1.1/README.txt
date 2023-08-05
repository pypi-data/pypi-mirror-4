Taskreport
==========

Taskreport is a simple tool to generate HTML reports from your Taskwarrior
task list and send them by email. 

The list of features includes:

* generating an html report containing the sections defined in the configuration file.
* sending the report to one or more email addresses (using the SMTP credentials
  defined in the configuration file).
* outputting the report to a local file.
* customizing the generated html with a template (using the Jinja template
  engine).
* inlining the CSS inside the HTML so that email clients which do not support
  external CSS can render the report gracefully.

Installation
------------

You have several options to install Taskreport:

* use ``pip install taskreport`` or ``easy_install taskreport`` to install
  directly from the Python Package Index.
* use ``python setup.py install`` from the package archive

**Note:** You will need to install Jinja to be able to use the templating feature
(this is optional).

Usage
-----

Configuration
~~~~~~~~~~~~~

A sample configuration file is distributed with this package and should be
located at ``share/config.sample``. All the configuration options are
commented. By default, ``taskreport`` tries to look at ``~/.taskreport`` for
the configuration file. You can specify another location by using the ``-c``
command-line option.

The configuration file contains: 

* a ``SMTP`` section for the SMTP credentials of the account to be used to send
  the report email
* a ``MAIL`` section to define the email subject and recipient(s)
* one section for each section to be included in the report: the section name
  in the configuration file will become the section title in the generated HTML.
  The section should only contain one ``filter`` option which should follow
  Taskwarrior's filtering syntax: this option will be fed directly to Taskwarrior
  to generate the list of tasks to include in the report.
* each section can also (optionally) include an ``order`` option to specify how
  the tasks should be ordered within a section. This option consists in
  a space-separated list of keys, each key followed by a plus or a minus sign.
  This indicates by order of precedence the key by which the tasks should be
  ordered. The plus or the minus sign indicates if the order for the key it is
  attached to should be increasing or decreasing. For example, ``priority-
  due-`` means that the tasks should be ordered by decreasing ``priority``, and
  in cases of ties by decreasing due date.

Command-line options
~~~~~~~~~~~~~~~~~~~~

The available command line options and their meaning can be found by typing
``taskreport -h``. Certain options can be defined both in the configuration
file and on the command-line. For those options, the command-line has
precedence over the configuration file.

Template
~~~~~~~~

Using a template is optional: Taskreport has a basic default layout. If you
wish to customize the layout, you can specify the location of a template file
by using the ``-t`` option on the command line.

The template file will be rendered by the Jinja template engine and thus must
comply to Jinja's syntax. You should refer to `Jinja's official documentation
<http://jinja.pocoo.org/docs/>`__ for more details.

The template file will receive as an environment variable a ``section_list``
variable. This is a list of dictionaries, one for each section. A section's
dictionary contains two keys: ``title`` for the section title, and
``task_list`` which is a JSON object containing the output you would get by
using Taskwarrior's export command with this section's filter rule.

A sample template file located at ``share/email_template.html`` should have
been distributed with this package. A more advanced template
``share/showcase_template.html`` is also included to showcase a more complex
scenario. The output produced by this template on a sample set of tasks can be
seen at ``share/showcase.html``.

Bugs, comments
--------------

This tool, although simple, might contain bugs or might be missing important
features. For bug reports or feature requests, feel free to contact us at
<task.report.python@gmail.com>.
