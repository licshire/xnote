# encoding=utf-8
import xtables
from xutils import SearchResult

def search(ctx, text):
    if not ctx.search_message:
        return
    db = xtables.get_message_table()
    msg_list = list(db.select(where="user=$user AND content like $key", order="ctime DESC",
        vars=dict(key='%' + text + '%', user=ctx.user_name), limit=1000))

    def convert(x):
        r = SearchResult()
        r.name = x.ctime
        r.url = '#'
        r.command = None
        r.raw = x.content
        return r
    return map(convert, msg_list)


