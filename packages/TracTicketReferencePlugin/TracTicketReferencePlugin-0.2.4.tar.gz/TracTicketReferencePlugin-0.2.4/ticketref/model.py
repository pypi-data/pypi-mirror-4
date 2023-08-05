# -*- coding: utf-8 -*-

from datetime import datetime

from trac.ticket.model import Ticket
from trac.util.datefmt import utc, to_utimestamp

from utils import cnv_list2text, cnv_sorted_refs, cnv_text2list

CUSTOM_FIELDS = [
    {
        "name": "ticketref",
        "type": "textarea",
        "properties": [
                        ("ticketref.label", "Relationships"),
                        ("ticketref.cols", "68"),
                        ("ticketref.rows", "1"),
        ],
    },
]
TICKETREF = CUSTOM_FIELDS[0]["name"]

UPDATE_TICKET = "UPDATE ticket SET changetime=%s WHERE id=%s"

SELECT_TICKETREF = "SELECT value FROM ticket_custom "\
                   "WHERE ticket=%%s AND name='%s'" % TICKETREF
INSERT_TICKETREF = "INSERT INTO ticket_custom (ticket, name, value) "\
                   "VALUES (%%s, '%s', %%s)" % TICKETREF
UPDATE_TICKETREF = "UPDATE ticket_custom SET value=%%s "\
                   "WHERE ticket=%%s AND name='%s'" % TICKETREF
DELETE_TICKETREF = "DELETE FROM ticket_custom "\
                   "WHERE ticket=%%s AND name='%s'" % TICKETREF

INSERT_TICKETCHG = "INSERT INTO ticket_change "\
                   "(ticket, time, author, field, oldvalue, newvalue) "\
                   "VALUES (%%s, %%s, %%s, '%s', %%s, %%s)" % TICKETREF


class TicketLinks(object):
    """A model for the ticket links as cross reference."""

    def __init__(self, env, ticket):
        self.env = env
        self.db = env.get_db_cnx()
        self.cursor = self.db.cursor()
        if not isinstance(ticket, Ticket):
            ticket = Ticket(self.env, ticket)
        self.ticket = ticket
        self.time_stamp = to_utimestamp(datetime.now(utc))

    def add_reference(self, refs):
        c = self.cursor
        for ref_id in refs:
            c.execute(SELECT_TICKETREF, (self.ticket.id,))
            row = c.fetchone()
            if row:
                target_refs = cnv_text2list(row[0])
                if not ref_id in target_refs:
                    target_refs.add(ref_id)
                    new_text = cnv_list2text(target_refs)
                    c.execute(UPDATE_TICKETREF, (new_text, self.ticket.id))
                    self.ticket[TICKETREF] = cnv_sorted_refs(
                                        self.ticket[TICKETREF], set([ref_id]))
            else:
                c.execute(INSERT_TICKETREF, (self.ticket.id, ref_id))
                self.ticket[TICKETREF] = u"%s" % ref_id

    def remove_cross_reference(self, refs, author):
        c = self.cursor
        for ref_id in refs:
            c.execute(SELECT_TICKETREF, (ref_id,))
            row = (c.fetchone() or ("",))[0]
            target_refs = cnv_text2list(row)
            target_refs.remove(self.ticket.id)
            if target_refs:
                new_text = cnv_list2text(target_refs)
                c.execute(UPDATE_TICKETREF, (new_text, ref_id))
            else:
                new_text = ""
                c.execute(DELETE_TICKETREF, (ref_id,))
            c.execute(INSERT_TICKETCHG, (
                ref_id, self.time_stamp, author, row.strip(), new_text))
            c.execute(UPDATE_TICKET, (self.time_stamp, ref_id))

    def add_cross_reference(self, refs, author):
        c = self.cursor
        for ref_id in refs:
            c.execute(SELECT_TICKETREF, (ref_id,))
            row = c.fetchone()
            if row:
                target_refs = cnv_text2list(row[0])
                if not self.ticket.id in target_refs:
                    target_refs.add(self.ticket.id)
                    new_text = cnv_list2text(target_refs)
                    c.execute(UPDATE_TICKETREF, (new_text, ref_id))
                    c.execute(INSERT_TICKETCHG, (ref_id, self.time_stamp,
                              author, row[0].strip(), new_text))
                    c.execute(UPDATE_TICKET, (self.time_stamp, ref_id))
            else:
                c.execute(INSERT_TICKETREF, (ref_id, self.ticket.id))
                c.execute(INSERT_TICKETCHG, (
                    ref_id, self.time_stamp, author, "", self.ticket.id))
                c.execute(UPDATE_TICKET, (self.time_stamp, ref_id))

    def create(self):
        refs = cnv_text2list(self.ticket[TICKETREF])
        self.add_cross_reference(refs, self.ticket["reporter"])
        self.db.commit()

    def change(self, author, old_refs_text):
        old_refs = cnv_text2list(old_refs_text)
        new_refs = cnv_text2list(self.ticket[TICKETREF])
        self.remove_cross_reference(old_refs - new_refs, author)
        self.add_cross_reference(new_refs - old_refs, author)
        self.db.commit()

    def delete(self):
        refs = cnv_text2list(self.ticket[TICKETREF])
        self.remove_cross_reference(refs, "admin")
        self.db.commit()
