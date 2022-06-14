#!/usr/bin/env python3
"""
Sometimes when I'm annotating using [[https://hypothes.is][Hypothesis]], I want to think more
about specific highlights, google more about them later or generally act on them somehow.

Normally you'd have to copy the URL, highlighted text and create a task from it.

This script does that automatically, only thing that you have to do is to mark it with a tag or type 'todo'
in the annotation text.

Items get scheduled and appear on my org-mode agenda,
so I can un/reschedule them if they don't require immediate attention.
"""

from orger import Queue
from orger.inorganic import node, link, timestamp
from orger.common import todo

from my.hypothesis import highlights, Highlight

from datetime import datetime,timezone

import re
from slugify import slugify

def org_slugify(text):
    text = slugify(text)
    text = re.sub(r'(\[[0-9]+%\])', '', text)
    text = re.sub(r'(\[[0-9]+/[0-9]+\])', '', text)
    text = re.sub(r'(\[#[ABC]\])', '', text)
    text = re.sub(r"\[\[\(.+?\)\]\[", '', text)
    text = re.sub(r"<[12][0-9]{3}-[0-9]{2}-[0-9]{2}\( .*?\)>", '', text)
    text = re.sub(r"<[12][0-9]{3}-[0-9]{2}-[0-9]{2}\( .*?\)>""\[[12][0-9]{3}-[0-9]{2}-[0-9]{2}( .*?)\]", '', text)
    return text

class HypTodos(Queue):
    def get_items(self) -> Queue.Results:
        index = 0
        for t in highlights():
            if isinstance(t, Exception):
                # todo make error helper work with Queue
                # probably hash of the body would be enough? dunno
                # I guess there isn't much we can do here? will be spotted by other tools
                continue
            index += 1
            ann = t.annotation
            hl = t.highlight or ''
            ts_utc0 = datetime.now(timezone.utc)
            today = datetime.now()
            if hl != '':
                body='#+BEGIN_QUOTE\n' + hl + '\n#+END_QUOTE\n'
            else:
                body=''

            yield t.hid, node(
                heading=f'Highlight from {link(title=t.title, url=t.url)}',
                properties = {
                    'ID': today.strftime('%F-%s-') + slugify(t.title) + '-' + str(index),
                    'URL': f'[[{t.hyp_link}][{t.url}]]',
                    'CREATED': timestamp(t.created, inactive=True),
                    'FC_CREATED': ts_utc0.strftime("%FT%TZ"),
                    'FC_TYPE': 'topic'
                },
                body,
                tags=['fc', *t.tags],
            )


if __name__ == '__main__':
    HypTodos.main()
