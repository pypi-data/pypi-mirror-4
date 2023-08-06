=============================
 Slick Python Client Library
=============================

This library is a python client for accessing and reporting results to Slick.  Slick is an
open source QA result and test manager available from http://code.google.com/p/slickqa.

Use is intended to be simple, and explorable.  All the types are defined, and code completion
will be available through most IDEs.  Here is an example of how the library is used::

  from slickqa import SlickConnection, Project

  slick = SlickConnection('http://localhost:8080')

  proj = slick.projects.findByName('A Project')
  release = slick.projects(proj).releases(proj.defaultRelease).get()

  print("The default release for project " + proj.name + " is " + release.name + ".")



