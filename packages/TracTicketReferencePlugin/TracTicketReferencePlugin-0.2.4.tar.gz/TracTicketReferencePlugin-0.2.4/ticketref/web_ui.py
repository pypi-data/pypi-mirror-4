# -*- coding: utf-8 -*-

from pkg_resources import resource_filename

from genshi.builder import tag
from trac.core import *
from trac.web.api import IRequestFilter, ITemplateStreamFilter
from trac.web.chrome import ITemplateProvider, add_script, add_stylesheet
from trac.resource import ResourceNotFound
from trac.ticket.model import Ticket
from trac.util.text import shorten_line
from trac.util.translation import domain_functions

from model import TICKETREF as TREF
from utils import cnv_text2list

_, add_domain = domain_functions("ticketref", ("_", "add_domain"))

TEMPLATE_FILES = [
    "report_view.html", "query_results.html", "ticket.html", "query.html",
]

COPY_TICKET_FIELDS = [
    "type", "priority", "milestone", "component", "version", "keywords",
    "owner", "cc",
]


class TicketRefsTemplate(Component):
    """ Extend template for ticket cross-reference """

    implements(IRequestFilter, ITemplateProvider, ITemplateStreamFilter)

    def __init__(self):
        add_domain(self.env.path, resource_filename(__name__, "locale"))

    # ITemplateStreamFilter methods
    def filter_stream(self, req, method, filename, stream, data):
        self.log.debug("TicketRefsTemplate: filter_stream start")
        if not data or (not filename in TEMPLATE_FILES):
            return stream

        # For ticket.html
        if "fields" in data and isinstance(data["fields"], list):
            self._filter_fields(req, data)

        # For query_results.html and query.html
        if "groups" in data and isinstance(data["groups"], list):
            self._filter_groups(req, data)

        # For report_view.html
        if "row_groups" in data and isinstance(data["row_groups"], list):
            self._filter_row_groups(req, data)

        self.log.debug("TicketRefsTemplate: filter_stream end")
        return stream

    def _filter_fields(self, req, data):
        for field in data["fields"]:
            if field["name"] == TREF:
                field["label"] = _("Relationships")
                ticket = data["ticket"]
                new = self._link_new(req, ticket, field)
                if ticket[TREF]:
                    field["rendered"] = self._link_refs(req, ticket[TREF],
                                                        verbose_link=True)
                    field["rendered"].append(new)
                else:
                    field["rendered"] = tag([new])

    def _filter_groups(self, req, data):
        fields_tref = data["fields"].get(TREF)
        fields_tref_type = ""
        if fields_tref:  # column checkbox/select option
            fields_tref["label"] = _("Relationships")
            fields_tref_type = fields_tref["type"]
        for header in data["headers"]:  # list view header
            if header["name"] == TREF:
                header["label"] = _("Relationships")
        for group, tickets in data["groups"]:
            for ticket in tickets:
                if TREF in ticket:
                    if fields_tref_type == u"textarea":
                        ticket[TREF] = self._link_textarea(req, ticket[TREF])
                    elif fields_tref_type == u"text":
                        ticket[TREF] = self._link_refs(req, ticket[TREF])

    def _filter_row_groups(self, req, data):
        for headers in data["header_groups"]:
            for header in headers:
                if header["col"] == TREF:
                    header["title"] = _("Relationships")
        for group, rows in data["row_groups"]:
            for row in rows:
                _is_list = isinstance(row["cell_groups"], list)
                if "cell_groups" in row and _is_list:
                    for cells in row["cell_groups"]:
                        for cell in cells:
                            if cell.get("header", {}).get("col") == TREF:
                                cell["value"] = self._link_refs(req,
                                                                cell["value"])

    def _link_refs(self, req, refs_text, verbose_link=False):
        items_tag = None
        items, verbose_items = [], []
        for ref_id in sorted(cnv_text2list(refs_text)):
            elem = verbose_elem = "#%s" % ref_id
            try:
                ticket = Ticket(self.env, ref_id)
                if "TICKET_VIEW" in req.perm(ticket.resource):
                    title = shorten_line(ticket["summary"])
                    attr = {
                        "class_": ticket["status"],
                        "href": req.href.ticket(ref_id),
                        "title": title,
                    }
                    elem = tag.a("#%s" % ref_id, **attr)
                    verbose_elem = tag.a("#%s %s" % (ref_id, title), **attr)
            except ResourceNotFound:
                pass  # not supposed to happen, just in case
            items.extend([elem, ", "])
            verbose_items.extend([verbose_elem, tag.br()])
        if items:
            items_tag = [tag.span(items[:-1], id="tref_ticketid")]
            if verbose_link:
                vattr = {"id": "tref_summary", "class_": "tref-display-none"}
                items_tag.append(tag.span(verbose_items[:-1], **vattr))
        return tag(items_tag)

    def _link_textarea(self, req, refs_text):
        items = []
        for ref_id in sorted(cnv_text2list(refs_text)):
            elem = u"#%s" % ref_id
            try:
                ticket = Ticket(self.env, ref_id)
                if "TICKET_VIEW" in req.perm(ticket.resource):
                    title = shorten_line(ticket["summary"])
                    elem = u"#%s %s" % (ref_id, title)
            except ResourceNotFound:
                pass  # not supposed to happen, just in case
            items.extend([elem, u", "])
        return u"".join(item for item in items[:-1])

    def _link_new(self, req, ticket, field):
        param = {TREF: ticket.id}
        for field in COPY_TICKET_FIELDS:
            if ticket[field]:
                param[field] = ticket[field]
        attr = {
            "class_": "tref-link",
            "target": "_blank",
            "href": req.href.newticket(**param),
            "title": _("Open new ticket with relationships"),
        }
        return tag.a(_("New"), **attr)

    # IRequestFilter methods
    def pre_process_request(self, req, handler):
        return handler

    def post_process_request(self, req, template, data, content_type):
        self.log.debug("TicketRefsTemplate: post_process_request, %s, %s" % (
                       req.path_info, template))
        if req.path_info.startswith("/ticket/"):
            add_stylesheet(req, "ticketref/ticket.css")
            add_script(req, "ticketref/ticket.js")
        return template, data, content_type

    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        yield ("ticketref", resource_filename(__name__, "htdocs"))

    def get_templates_dirs(self):
        return []
