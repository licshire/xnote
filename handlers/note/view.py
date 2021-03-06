# -*- coding:utf-8 -*-
# @author xupingmao
# @since 2016/12
# @modified 2018/03/06 23:32:42

import profile
import math
import re
import web
import xauth
import xutils
import xconfig
import xtables
import xtemplate
import xmanager
from web import HTTPError
from . import dao
from xconfig import Storage
from xutils import History
config = xconfig

PAGE_SIZE = xconfig.PAGE_SIZE

@xmanager.listen("note.view", is_async=True)
def visit_by_id(ctx):
    id = ctx.id
    db = xtables.get_file_table()
    sql = "UPDATE file SET visited_cnt = visited_cnt + 1, atime=$atime where id = $id"
    db.query(sql, vars = dict(atime = xutils.format_datetime(), id=id))

class ViewHandler:

    xconfig.note_history = History("笔记浏览记录", 200)

    def GET(self, op):
        id   = xutils.get_argument("id", "")
        name = xutils.get_argument("name", "")
        page = xutils.get_argument("page", 1, type=int)
        pagesize = xutils.get_argument("pagesize", xconfig.PAGE_SIZE, type=int)
        db   = xtables.get_file_table()
        user_name = xauth.get_current_name()
        show_add_file = False

        if id == "" and name == "":
            raise HTTPError(504)
        if id != "":
            id = int(id)
            file = dao.get_by_id(id, db=db)
        elif name is not None:
            file = dao.get_by_name(name, db=db)
        if file is None:
            raise web.notfound()
        
        if not file.is_public and user_name != "admin" and user_name != file.creator:
            raise web.seeother("/unauthorized")
        show_search_div = False
        pathlist = dao.get_pathlist(db, file)
        can_edit = (file.creator == user_name) or (user_name == "admin")
        role = xauth.get_current_role()

        # 定义一些变量
        files = []
        amount = 0
        template_name = "note/view.html"
        xconfig.note_history.put(dict(user=user_name, file_id = id, name = file.name))

        if file.type == "group":
            amount = db.count(where="parent_id=$id AND is_deleted=0 AND creator=$creator", 
                vars=dict(id=file.id, creator=user_name))
            files = db.select(where=dict(parent_id=file.id, is_deleted=0, creator=user_name), 
                order="priority DESC, name", 
                limit=pagesize, 
                offset=(page-1)*pagesize)
            content = file.content
            show_search_div = True
            show_add_file = True
        elif file.type == "md" or file.type == "text":
            content = file.content
            if op == "edit":
                template_name = "note/markdown_edit.html"
        else:
            content = file.content
            content = content.replace(u'\xad', '\n')
            content = content.replace(u'\n', '<br/>')
            file.data = file.data.replace(u"\xad", "\n")
            file.data = file.data.replace(u'\n', '<br/>')
            if file.data == None or file.data == "":
                file.data = content
        
        xmanager.fire("note.view", file)
        return xtemplate.render(template_name,
            file=file, 
            op=op,
            show_add_file = show_add_file,
            can_edit = can_edit,
            pathlist = pathlist,
            page_max = math.ceil(amount/pagesize),
            page = page,
            page_url = "/file/view?id=%s&page=" % id,
            files = files)

def sqlite_escape(text):
    if text is None:
        return "NULL"
    if not (isinstance(text, str)):
        return repr(text)
    text = text.replace("'", "''")
    return "'" + text + "'"

def result(success = True, msg=None):
    return {"success": success, "result": None, "msg": msg}

def is_img(filename):
    name, ext = os.path.splitext(filename)
    return ext.lower() in (".gif", ".png", ".jpg", ".jpeg", ".bmp")

def get_link(filename, webpath):
    if is_img(filename):
        return "![%s](%s)" % (filename, webpath)
    return "[%s](%s)" % (filename, webpath)

class UpdateHandler:

    @xauth.login_required()
    def POST(self):
        is_public = xutils.get_argument("public", "")
        id        = xutils.get_argument("id", type=int)
        content   = xutils.get_argument("content")
        version   = xutils.get_argument("version", type=int)
        file_type = xutils.get_argument("type")
        name      = xutils.get_argument("name", "")

        file = dao.get_by_id(id)
        assert file is not None

        # 理论上一个人是不能改另一个用户的存档，但是可以拷贝成自己的
        # 所以权限只能是创建者而不是修改者
        update_kw = dict(content=content, 
                type=file_type, 
                size=len(content));

        if name != "" and name != None:
            update_kw["name"] = name

        # 不再处理文件，由JS提交
        rowcount = dao.update(where = dict(id=id, version=version), **update_kw)
        if rowcount > 0:
            xmanager.fire('note.updated', update_kw)
            raise web.seeother("/file/view?id=" + str(id))
        else:
            # 传递旧的content
            cur_version = file.version
            file.content = content
            file.version = version
            return xtemplate.render("note/view.html", file=file, 
                content = content, 
                children = [],
                error = "更新失败, version冲突,当前version={},最新version={}".format(version, cur_version))

class Upvote:

    @xauth.login_required()
    def GET(self, id):
        id = int(id)
        db = xtables.get_file_table()
        file = db.select_one(where=dict(id=int(id)))
        db.update(priority=1, where=dict(id=id))
        raise web.seeother("/file/view?id=%s" % id)

class Downvote:
    @xauth.login_required()
    def GET(self, id):
        id = int(id)
        db = xtables.get_file_table()
        file = db.select_one(where=dict(id=int(id)))
        db.update(priority=0, where=dict(id=id))
        raise web.seeother("/file/view?id=%s" % id)

class RenameHandler:

    @xauth.login_required()
    def POST(self):
        id = xutils.get_argument("id")
        name = xutils.get_argument("name")
        if name == "" or name is None:
            return dict(code="fail", message="名称为空")
        db = xtables.get_file_table()
        old  = db.select_one(where=dict(id=id))
        if old.creator != xauth.get_current_name():
            return dict(code="fail", message="没有权限")

        file = db.select_one(where=dict(name=name))
        if file is not None:
            return dict(code="fail", message="%r已存在" % name)
        db.update(where=dict(id=id), name=name, mtime=xutils.format_datetime())
        return dict(code="success")

    def GET(self):
        return self.POST()

class FileSaveHandler:

    @xauth.login_required()
    def POST(self):
        content = xutils.get_argument("content", "")
        data    = xutils.get_argument("data", "")
        id = xutils.get_argument("id", "0", type=int)
        type = xutils.get_argument("type")
        name = xauth.get_current_name()
        db = xtables.get_file_table()
        where = None
        if xauth.is_admin():
            where=dict(id=id)
        else:
            where=dict(id=id, creator=name)
        kw = dict(size=len(content), mtime=xutils.format_datetime(), 
            where=where)
        if type == "html":
            kw["data"] = data
            kw["content"] = data
            if xutils.bs4 is not None:
                soup = xutils.bs4.BeautifulSoup(data, "html.parser")
                content = soup.get_text(separator=" ")
                kw["content"] = content
            kw["size"] = len(content)
        else:
            kw["content"] = content
            kw["size"] = len(content)
        rowcount = db.update(**kw)
        if rowcount > 0:
            return dict(code="success")
        else:
            return dict(code="fail")

class MarkHandler:

    def GET(self):
        id = xutils.get_argument("id")
        db = xtables.get_file_table()
        db.update(is_marked=1, where=dict(id=id))
        raise web.seeother("/file/view?id=%s"%id)

class UnmarkHandler:
    def GET(self):
        id = xutils.get_argument("id")
        db = xtables.get_file_table()
        db.update(is_marked=0, where=dict(id=id))
        raise web.seeother("/file/view?id=%s"%id)
        
class LibraryHandler:

    def GET(self):
        return xtemplate.render("note/library.html")

class DictHandler:

    def GET(self):
        page = xutils.get_argument("page", 1, type=int)
        db = xtables.get_dict_table()
        items = db.select(order="id", limit=PAGE_SIZE, offset=(page-1)*PAGE_SIZE)
        def convert(item):
            v = Storage()
            v.name = item.key
            v.summary = item.value
            v.mtime = item.mtime
            v.ctime = item.ctime
            v.url = "#"
            return v
        items = map(convert, items)
        count = db.count()
        page_max = math.ceil(count / PAGE_SIZE)

        return xtemplate.render("note/view.html", 
            files = list(items), 
            file_type = "group",
            show_opts = False,
            page = page,
            page_max = page_max,
            page_url = "/file/dict?page=")

xurls = (
    r"/file/(edit|view)", ViewHandler, 
    r"/note/(edit|view)", ViewHandler,
    r"/file/rename", RenameHandler,
    r"/file/update", UpdateHandler,
    r"/file/save", FileSaveHandler,
    r"/file/autosave", FileSaveHandler,
    r"/file/(\d+)/upvote", Upvote,
    r"/file/(\d+)/downvote", Downvote,
    r"/file/mark", MarkHandler,
    r"/file/unmark", UnmarkHandler,
    r"/file/markdown", ViewHandler,
    r"/file/library", LibraryHandler,
    r"/file/dict", DictHandler
)

