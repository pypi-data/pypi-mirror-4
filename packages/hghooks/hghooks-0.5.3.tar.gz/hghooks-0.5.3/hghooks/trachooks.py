# Copyright (c) 2010 by Yaco Sistemas <lgs@yaco.es>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import re

from pkg_resources import iter_entry_points

try:
    from trac.env import open_environment
    from trac.ticket import Ticket
    from trac.ticket.notification import TicketNotifyEmail
    from trac.ticket.web_ui import TicketModule
    from trac.util.datefmt import utc
    HAS_TRAC = True
except ImportError:
    HAS_TRAC = False

from hghooks import CheckerManager


def close(ticket):
    ticket['status'] = 'closed'
    ticket['resolution'] = 'fixed'


def noop(*args, **kwargs):
    pass


def default_ticket_commands():
    return {
        'close': close,
        'closed': close,
        'closes': close,
        'fix': close,
        'fixed': close,
        'fixes': close,
        'addresses': noop,
        'references': noop,
        'refs': noop,
        're': noop,
        'see': noop,
        }


def merge(token, ticket):
    ticket['merged_in'] = token


def default_token_commands():
    return {
        'merge in': merge,
        'merged in': merge,
        }


def utc_time():
    return datetime.datetime.utcnow().replace(tzinfo=utc)


def load_ticket_commands():
    ticket_commands = {}
    for entry_point in iter_entry_points(group='hghooks.trac.ticket_commands'):
        plugin = entry_point.load()
        ticket_commands.update(plugin())

    return ticket_commands


def load_token_commands():
    token_commands = {}
    for entry_point in iter_entry_points(group='hghooks.trac.token_commands'):
        plugin = entry_point.load()
        token_commands.update(plugin())

    return token_commands


ticket_prefix = '(?:#|(?:ticket|issue|bug)[: ]?)'
ticket_reference = ticket_prefix + '[0-9]+'
ticket_command = (r'(?P<action>[A-Za-z]*).?'
                  '(?P<ticket>%s(?:(?:[, &]*|[ ]?and[ ]?)%s)*)' %
                  (ticket_reference, ticket_reference))

command_re = re.compile(ticket_command)
ticket_re = re.compile(ticket_prefix + '([0-9]+)')
token_re = re.compile(r'(\w+)')


def get_ticket_commands(msg):
    """Associate a list of commands for each ticket in the msg"""
    ticket_commands = load_ticket_commands()

    tickets = {}
    for cmd, tkts in command_re.findall(msg):
        command = ticket_commands.get(cmd.lower(), None)
        if callable(command):
            for tkt_id in ticket_re.findall(tkts):
                tickets.setdefault(tkt_id, []).append(command)

    return tickets


class TicketChecker(object):

    error_msg = 'At least one open ticket must be mentioned in the log message'

    def __init__(self, trac_env, ticket_words, ui):
        self.trac_env = trac_env
        self.ticket_words = ticket_words
        self.ui = ui

    def __call__(self, files_to_check, msg):
        warnings = 0

        tickets = get_ticket_commands(msg).keys()

        if tickets == []:
            self.ui.warn(self.error_msg + '\n')
            warnings += 1
        else:
            env = open_environment(self.trac_env)
            db = env.get_db_cnx()

            cursor = db.cursor()
            cursor.execute("SELECT COUNT(id) FROM ticket WHERE "
                           "status <> 'closed' AND id IN (%s)" %
                           ','.join(tickets))
            row = cursor.fetchone()
            if not row or row[0] < 1:
                self.ui.warn(self.error_msg + '\n')
                warnings += 1

        return warnings


def ticket_checker(ui, repo, hooktype, node, pending, **kwargs):
    if not HAS_TRAC:
        ui.warn('You need the trac python package to use the ticket_checker')
        return True  # failure

    checker_manager = CheckerManager(ui, repo, node)
    trac_env = ui.config('trac', 'environment')
    if trac_env is None:
        ui.warn('You must set the environment option in the [trac] section'
                ' of the repo configuration to use this hook')
        return True  # failure

    ticket_commands = load_ticket_commands()
    ticket_words = ticket_commands.keys()

    return checker_manager.check(TicketChecker(trac_env, ticket_words, ui))


class TicketUpdater(object):

    def __init__(self, trac_env, repo_name, changeset_style, msg_template, ui):
        self.trac_env = trac_env
        self.repo_name = repo_name
        self.changeset_style = changeset_style
        self.msg_template = msg_template
        self.ui = ui

    def execute_ticket_commands(self, tickets, env):
        """Run the commands associated with ticket and return the list
        of processed ticket objects (trac.ticket.Ticket)"""
        processed_tickets = []
        for tkt_id, cmds in tickets.iteritems():
            try:
                db = env.get_db_cnx()

                ticket = Ticket(env, int(tkt_id), db)
                for cmd in cmds:
                    cmd(ticket)
                processed_tickets.append(ticket)
            except Exception, e:
                self.ui.warn('Unexpected error while processing ticket %s: %s'
                             % (tkt_id, e))
        return processed_tickets

    def execute_token_commands(self, msg, processed_tickets):
        """token commands processing"""
        for match_str, token_cmd in load_token_commands().items():
            index = msg.find(match_str)
            if index != -1:
                found_str = msg[index + len(match_str) + 1:]
                match = token_re.match(found_str)
                if match:
                    token = match.groups()[0]
                    for ticket in processed_tickets:
                        token_cmd(token, ticket)

    def get_ticket_changelog_size(self, ticket, tmodule, db):
        """Determine sequence number"""
        return len([change
                    for change in tmodule.grouped_changelog_entries(ticket, db)
                    if change['permanent']])

    def save_and_notify(self, processed_tickets, env, author, msg, date):
        db = env.get_db_cnx()
        tmodule = TicketModule(env)
        tnotify = TicketNotifyEmail(env)
        for ticket in processed_tickets:
            cnum = self.get_ticket_changelog_size(ticket, tmodule, db)
            ticket.save_changes(author, msg, date, db, cnum + 1)
            db.commit()
            tnotify.notify(ticket, newticket=0, modtime=date)

    def compose_msg(self, changes):
        msg = []
        for changectx in changes:
            styles = {
                'number': changectx.rev(),
                'long-hex': changectx.hex()
                }
            styles['short-hex'] = styles['long-hex'][:12]

            try:
                changeset = styles[self.changeset_style]
            except KeyError:
                self.ui.warn('Unsupported changeset style: "%s". Currently '
                             'supported are: number, short-hex and long-hex.'
                             'Using default (short-hex)'
                             % self.changeset_style)
                changeset = styles['short-hex']

            if self.repo_name is not None:
                changeset += u'/' + self.repo_name

            msg.append(self.msg_template % {
                    'changeset': changeset,
                    'msg': unicode(changectx.description(), 'utf-8'),
                    })

        return u'\n'.join(msg)

    def __call__(self, changes):
        msg = self.compose_msg(changes)

        tickets = get_ticket_commands(msg)

        env = open_environment(self.trac_env)

        processed_tickets = self.execute_ticket_commands(tickets, env)
        self.execute_token_commands(msg, processed_tickets)

        author = unicode(changes[0].user(), 'utf-8')
        date = utc_time()
        self.save_and_notify(processed_tickets, env, author, msg, date)


def ticket_updater(ui, repo, hooktype, node, source, url):
    if not HAS_TRAC:
        ui.warn('You need the trac python package to use the ticket_updater')
        return True  # failure

    trac_env = ui.config('trac', 'environment')
    if trac_env is None:
        ui.warn('You must set the environment option in the [trac] section'
                ' of the repo configuration to use this hook')
        return True  # failure

    repo_name = ui.config('trac', 'repo_name', None)
    changeset_style = ui.config('trac', 'changeset_style', 'short-hex')
    msg_template = ui.config('trac', 'msg_template',
                             '(At [%(changeset)s]) %(msg)s')
    msg_template = unicode(msg_template, 'utf-8')

    if hooktype == 'changegroup':
        # fetch all remaining changesets
        changes = [repo[rev]
                   for rev in range(repo[node].rev(), len(repo.changelog))]
    else:
        # use just the current revision
        changes = [repo[node]]

    ticket_updater = TicketUpdater(trac_env, repo_name, changeset_style,
                                   msg_template, ui)
    ticket_updater(changes)
