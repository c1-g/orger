#!/usr/bin/env python3
"""
Better interface for reading saved reddit posts/comments
"""
from orger import Queue
from orger.inorganic import node, link, Quoted
from orger.common import dt_heading

from my.reddit.all import saved

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


class RedditView(Queue):
    def get_items(self) -> Queue.Results:
        for s in saved():
            if s.text.strip() != '':
                body="#+BEGIN_SRC markdown\n" + s.text + "\n#+END_SRC"
            else:
                body=''
                
            yield s.sid, node(
                # need to make heading lazy due to is_alive
                # eh, can't guess the type of lambda??
                heading=lambda s=s: dt_heading( # type: ignore[misc]
                    s.created,
                    ('[#A] *DEAD*' if self.is_dead_url(s.url) else '') + link(title=s.title, url=s.url) + f' /r/{s.subreddit}'
                ),
                properties = {
                    'ID': today.strftime('%F-%s-') + slugify(s.title),
                    'CREATED': timestamp(t.created, inactive=True),
                    'FC_CREATED': ts_utc0.strftime("%FT%TZ"),
                    'FC_TYPE': 'topic'
                },
                body,
                tags=['fc'],
            )

    # todo this could be generic, i.e. checking all urls?
    def is_dead_url(self, url: str) -> bool:
        assert self.cmdline_args is not None
        # TODO this is probably easier to control via env variables, more malleable
        if not self.cmdline_args.mark_dead:
            return False
        from kython.knetwork import is_alive # type: ignore
        return is_alive(url)
        # todo should somehow track handle DELETED comments...
        # sometimes it's also [removed]
        # TODO maybe, track that in reddit provider? since we have all version of saved items over time


def setup_parser(p) -> None:
    p.add_argument(
        '--mark-dead',
        action='store_true',
        help="Mark deleted/unavailable content so you could process it ASAP. Mostly useful on first run",
    )

if __name__ == '__main__':
    RedditView.main(setup_parser=setup_parser)



# TODO actually might be useful to store forever a read only version...
# eh, turned out easier to make it lazy..
# def get_saves_with_state():
#     # TODO don't query for dead so often. We actually only want to get it for new items..
#     saves = get_saves(all_=False)
#     with Pool() as p:
#         res = p.map(_helper, saves)
#     dead = [r for r, s in res if not s]
#     # if len(dead) / (len(saves) + 1) > 0.3:
#     #     raise RuntimeError('something must be wrong with reddit! bailing')
#     return res

