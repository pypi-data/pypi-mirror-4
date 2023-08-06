"""
slick.py is a library for talking to slick (http://code.google.com/p/slickqa).

Copyright 2013 AccessData Group, LLC.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from . import micromodels

class Configuration(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    configurationType = micromodels.StringField()
    filename = micromodels.StringField()

    # Using BaseField for now as a way of holding a dictionary field
    configurationData = micromodels.BaseField()

class Build(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    built = micromodels.DateTimeField(use_int=True)

class Release(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    target = micromodels.DateTimeField(use_int=True)
    defaultBuild = micromodels.StringField()
    builds = micromodels.ModelCollectionField(Build)

class Component(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    description = micromodels.StringField()
    code = micromodels.StringField()

class DataDrivenPropertyType(micromodels.Model):
    name = micromodels.StringField()
    requirement = micromodels.BooleanField()
    standardValues = micromodels.FieldCollectionField(micromodels.StringField)

class Project(micromodels.Model):
    id = micromodels.StringField()
    name = micromodels.StringField()
    description = micromodels.StringField()
    configuration = micromodels.ModelField(Configuration)
    defaultRelease = micromodels.StringField()
    releases = micromodels.ModelCollectionField(Release)
    inactiveReleases = micromodels.ModelCollectionField(Release)
    lastUpdated = micromodels.DateTimeField(use_int=True)
    tags = micromodels.FieldCollectionField(micromodels.StringField())
    attributes = micromodels.BaseField()
    automationTools = micromodels.FieldCollectionField(micromodels.StringField())
    components = micromodels.ModelCollectionField(Component)
    datadrivenProperties = micromodels.ModelCollectionField(DataDrivenPropertyType)






