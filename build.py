import os
import jinja2
import markdown
import pathlib
from datetime import datetime
from dataclasses import dataclass


__here__ = pathlib.Path(__file__).resolve().parent


date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


md = markdown.Markdown(extensions=['meta', "toc"])


env = jinja2.Environment(loader = jinja2.FileSystemLoader(str(__here__ / "templates")))


# grab yeps --------------------------------------------------------------------------------------


@dataclass
class YEP:
    index: int
    title: str
    author: str
    status: str
    yep_type: str
    #yaq_version: str
    content: str


yeps = []
for yep in os.listdir(__here__ / "yeps"):
    with open(__here__ / "yeps" / yep, "r") as f:
        s = f.read()
        s = s.replace("# Abstract", "# Table of Contents\n[TOC]\n# Abstract")  # hack
        content = md.convert(s)
        kwargs = dict()
        kwargs["index"] = md.Meta["yep"][0]
        kwargs["title"] = md.Meta["title"][0]
        kwargs["author"] = md.Meta["author"][0]
        kwargs["status"] = md.Meta["status"][0]
        kwargs["yep_type"] = md.Meta["type"][0]
        #kwargs["yaq_version"] = md.Meta["yaq version"][0]
        kwargs["content"] = content
        yeps.append(YEP(**kwargs))


yeps.sort(key=lambda y: y.index)


# index -------------------------------------------------------------------------------------------


if not os.path.isdir(__here__ / "public"):
    os.mkdir(__here__ / "public")


template = env.get_template("index.html")
with open(__here__ / "public" / "index.html", "w") as f:
    f.write(template.render(yeps=yeps, title="yaq enhancement proposals", date=date))


# posts -------------------------------------------------------------------------------------------


template = env.get_template("yep.html")
for yep in yeps:
    if not os.path.isdir(__here__ / "public" / yep.index):
        os.mkdir(__here__ / "public" / yep.index)
    with open(__here__ / "public" / yep.index / "index.html", "w") as f:
        f.write(template.render(yep=yep, title=yep.title, date=date))


# css ---------------------------------------------------------------------------------------------


template = env.get_template('style.css')
for d, _, _ in os.walk(__here__ / "public", topdown=False):
    with open(os.path.join(d, "style.css"), 'w') as f:
        f.write(template.render())
