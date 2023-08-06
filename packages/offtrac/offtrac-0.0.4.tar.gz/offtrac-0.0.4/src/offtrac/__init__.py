# offtrac - a Python interface to trac using xmlrpclib.
#
# Copyright (C) 2008 Red Hat Inc.
# Author: Jesse Keating <jkeating@redhat.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import xmlrpclib

class TracServer(object):
    """The base Trac xmlrpc server object to interact with"""

    def __init__(self, uri):
        """Create an xmlrpc object.  Set self.server to this object but allow
        for later things to be re-assigned to self.server without losing the
        xmlrpc object.  This is useful for multicall.

        """

        self._xmlrpcserver = xmlrpclib.ServerProxy(uri)
        self.server = self._xmlrpcserver

    def setup_multicall(self):
        """Create a multicallable xmlrpc object. and assign it to
        self.server.  Other api calls use self.server and will automatically
        become multicall if this is set.

        """

        self.server = xmlrpclib.MultiCall(self._xmlrpcserver)

    def do_multicall(self):
        """Do the multicall and reset self.server to be non-multicall."""

        results = self.server()
        self.server = self._xmlrpcserver
        return results

    def query_tickets(self, query):
        """Query the ticket list based on a structured query string.
        Returns a list of ticket numbers matching the query.

        """
        return self.server.ticket.query(query)

    def list_milestones(self):
        """Return a list of milestones."""

        # TODO: this should optionally filter out closed milestones.
        return self.server.ticket.milestone.getAll()

    def get_ticket(self, ticket):
        """Returns a list of tickets (one?) that is itself a list of the
        ticket info.

        """

        return self.server.ticket.get(ticket)

    def get_milestone(self, milestone):
        """Returns a list of milestones (one?) that is a dict of the
        milestone info.

        """

        return self.server.ticket.milestone.get(milestone)

    def create_ticket(self, summary, description, type=None, priority=None,
                      milestone=None, component=None, version=None,
                      keywords=None, assignee=None, cc=None, notify=False,
                      owner=None):
        """Create a new ticket using information passed, optionally with
        notifications.
        summary and description are required.
        Returns the new ticket number if successful

        """

        # Build up a dict of our attributes
        arglist = ('type', 'priority', 'milestone', 'component', 'version',
                   'keywords', 'assignee', 'cc', 'owner')
        attributes = {}
        args = locals()
        for attribute in args: # locals is a list of the local variables
            if attribute in arglist:
                if args[attribute] == None:
                    continue
                attributes[attribute] = args[attribute]

        # There really is no such concept as an "assignee".
        # Keep it around for backwards compatibility.
        # https://bugzilla.redhat.com/show_bug.cgi?id=836514
        if not attributes.get('owner') and attributes.get('assignee'):
            attributes['owner'] = attributes['assignee']

        return self.server.ticket.create(summary,
                                         description,
                                         attributes,
                                         notify)

    def update_ticket(self, ticket, comment='', summary=None, type=None,
                      description=None, priority=None, milestone=None,
                      component=None, version=None, keywords=None, cc=None,
                      status=None, resolution=None, owner=None, notify=False):
        """Modify a ticket using information passed, optionally with
        notifications.
        Ticket number and one other argument required.
        Returns the new ticket info if successful

        """

        # TODO: Validate various fields like type, priority, milestone,
        # component, version for what's accepted in the project space.
        # There is no validation of this server side so we can really screw
        # things up here.
        # TODO: closing tickets doesn't seem to work.  Why?

        # Build up a dict of our attributes
        arglist = ('summary', 'type', 'description', 'priority', 'milestone',
                   'component', 'version', 'keywords', 'cc', 'status',
                   'resolution', 'owner')
        attributes = {}
        args = locals()
        for attribute in args: # locals is a list of the local variables
            if attribute in arglist:
                if args[attribute] == None:
                    continue
                attributes[attribute] = args[attribute]
        return self.server.ticket.update(ticket, comment, attributes, notify)

    def create_milestone(self, name, description=None, due=None):
        """Create a new milestone using information passed.
        Only name is required.
        Returns 0 if successful

        """

        attributes = {}
        if description:
            attributes['description'] = description
        if due:
            attributes['due'] = due

        return self.server.ticket.milestone.create(name, attributes)
