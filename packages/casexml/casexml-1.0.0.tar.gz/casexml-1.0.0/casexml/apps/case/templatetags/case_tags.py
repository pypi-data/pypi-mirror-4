from functools import partial
import copy
import datetime

from django import template
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _
from django.utils.safestring import mark_safe
from django.utils.html import escape

import pytz
import simplejson

from corehq.apps.hqwebapp.templatetags.proptable_tags import (
    get_tables_as_columns, get_definition)


register = template.Library()


DYNAMIC_CASE_PROPERTIES_COLUMNS = 4


@register.simple_tag
def render_case(case, options):
    """
    Uses options since Django 1.3 doesn't seem to support templatetag kwargs.
    Change to kwargs when we're on a version of Django that does.
    
    """
    timezone = options.get('timezone', pytz.utc)
    _get_tables_as_columns = partial(get_tables_as_columns, timezone=timezone)
    display = options.get('display', None)

    display = display or [
        {
            "layout": [
                [
                    {
                        "expr": "name",
                        "name": _("Name"),
                    },
                    {
                        "expr": "opened_on",
                        "name": _("Opened On"),
                        "parse_date": True,
                    },
                    {
                        "expr": "modified_on",
                        "name": _("Modified On"),
                        "parse_date": True,
                    },
                    {
                        "expr": "closed_on",
                        "name": _("Closed On"),
                        "parse_date": True,
                    },
                ],
                [
                    {
                        "expr": "type",
                        "name": _("Case Type"),
                        "format": '<code>{0}</code>',
                    },
                    {
                        "expr": "user_id",
                        "name": _("User ID"),
                        "format": '<span data-field="user_id">{0}</span>',
                    },
                    {
                        "expr": "owner_id",
                        "name": _("Owner ID"),
                        "format": '<span data-field="owner_id">{0}</span>',
                    },
                    {
                        "expr": "_id",
                        "name": _("Case ID"),
                    },
                ],
            ],
        }
    ]

    data = copy.deepcopy(case.to_json())

    default_properties = _get_tables_as_columns(data, display)

    # pop seen properties off of remaining case properties
    dynamic_data = dict(case.dynamic_case_properties())
    for section in display:
        for row in section['layout']:
            for item in row:
                dynamic_data.pop(item.get("expr"), None)

    dynamic_keys = sorted(dynamic_data.keys())
    definition = get_definition(
            dynamic_keys, num_columns=DYNAMIC_CASE_PROPERTIES_COLUMNS)

    dynamic_properties = _get_tables_as_columns(dynamic_data, definition)

    actions = case.to_json()['actions']
    actions.reverse()

    tz_abbrev = timezone.localize(datetime.datetime.now()).tzname()

    return render_to_string("case/partials/single_case.html", {
        "default_properties": default_properties,
        "default_properties_options": {
            "style": "table"
        },
        "dynamic_properties": dynamic_properties,
        "dynamic_properties_options": {
            "style": "table"
        },
        "case": case,
        "case_actions": mark_safe(simplejson.dumps(actions)),
        "timezone": timezone,
        "tz_abbrev": tz_abbrev
    })
    
    
@register.simple_tag
def case_inline_display(case):
    """
    Given a case id, make a best effort at displaying it.
    """
    if case:
        if case.opened_on:
            ret = "%s (%s: %s)" % (case.name, _("Opened"), case.opened_on.date())
        else:
            ret =  case.name
    else:
        ret = _("Empty Case")

    return escape(ret)
    
