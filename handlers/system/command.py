# encoding=utf-8
# @author xupingmao
# @modified 2018/02/15 10:46:19

import web
import os
import xutils
import subprocess
import xauth


class OpenDirHandler:
    @xauth.login_required("admin")
    def GET(self):
        path = xutils.get_argument("path")
        if os.path.isdir(path):
            path = '"%s"' % path
            if xutils.is_windows():
                path = path.replace("/", "\\")
                cmd = "explorer %s" % path
            elif xutils.is_mac():
                cmd = "open %s" % path
        else:
            cmd = path
        print(cmd)
        os.popen(cmd)
        return "<html><script>window.close()</script></html>"

    def POST(self):
        return self.GET()

class CommandHandler:

    command_list = {
        "open_xnote_dir": "explorer .",
        "shutdown": "shutdown /s /t 60",
    }

    @xauth.login_required("admin")
    def GET(self):
        command = xutils.get_argument("command", "")
        path    = xutils.get_argument("path", "")
        # command = xutils.readfile(path)
        # subprocess和os.popen不能执行多条命令(win32)
        # subprocess在IDLE下会创建新的会话窗口，cmd下也不会创建新窗口
        # subprocess执行命令不能换行
        # os.popen可以执行系统命令
        # os.popen就是subprocess.Popen的封装
        print(command, path)
        if command == "openTerminal":
            if xutils.is_mac():
                # TODO
                pass
            if xutils.is_windows():
                os.popen("start; cd \"%s\"" % path)
            return "success"
        if path.endswith(".bat"):
            os.popen("start %s" % path)
        else:
            os.popen(path)
        # os.popen(command)
        return "success"

    @xauth.login_required("admin")
    def POST(self):
        bufsize = 1024
        input_str = xutils.get_argument("command")
        try:
            fp = os.popen(input_str)
            buf = fp.read(bufsize)
            while buf:
                yield buf
                buf = fp.read(bufsize)
        finally:
            fp.close()

class PythonCommandHandler:

    @xauth.login_required("admin")
    def POST(self):
        content = xutils.get_argument("content")
        result = xutils.exec_python_code("<shell>", content)
        return dict(code="success", message="", data=result)

xurls = (
    r"/system/command", CommandHandler,
    r"/system/command/open", OpenDirHandler,
    r"/system/command/python", PythonCommandHandler,
)
