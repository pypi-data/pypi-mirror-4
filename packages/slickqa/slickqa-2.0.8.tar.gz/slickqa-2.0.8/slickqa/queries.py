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
__author__ = 'Jason Corbett'
__author__ = 'jcorbett'

from . import micromodels

class SlickQuery(micromodels.Model):
    """Base class for all query classes.  Query classes aren't used by slick, but are a way of documenting which
    query options are available for various endpoints."""

    def __init__(self):
        super(SlickQuery, self).__init__()


class ConfigurationQuery(SlickQuery):
    """Configuration Query options.  There are 3:
     * name: You can query for the configuration by Name.
     * configurationType: Although this is a string (on the server side as well), there are a few known configuration
       types: PROJECT, and ENVIRONMENT.  You probably won't query for PROJECT types, as they are automatically included
       in the project itself.
     * filename: This corresponds to the filename parameter of the configuration data type.  It is not directly used
       by the server for anything, but is an additional way to distinguish one configuration from another.
    """
    name = micromodels.StringField()
    configurationType = micromodels.StringField()
    filename = micromodels.StringField()

    def __init__(self, name=None, configurationType=None, filename=None):
        """Create a new configuration query, optionally specifying the parameters"""
        super(ConfigurationQuery, self).__init__()

        if name is not None:
            self.name = name
        if configurationType is not None:
            self.configurationType = configurationType
        if filename is not None:
            self.filename = filename
