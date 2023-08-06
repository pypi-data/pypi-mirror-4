# Copyright 2012 - John Calixto
#
# This file is part of bang.
#
# bang is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bang is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bang.  If not, see <http://www.gnu.org/licenses/>.
"""
Constants for attribute names of the various resources.

Just a place to stash more magic strings.
"""
from . import creds, server, secgroup, tags, database, ssh_key, loadbalancer

# stack attributes
NAME = 'name'
VERSION = 'version'
LOGGING = 'logging'
PLAYBOOKS = 'playbooks'
STACK = 'stack'
DEPLOYER_CREDS = 'deployer_credentials'
KEY = 'key'
SERVER_CLASS = 'server_class'
PROVIDER = 'provider'
