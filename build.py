#! /usr/bin/env python3

import os
import jinja2
import markdown
import pathlib
from datetime import datetime
from dataclasses import dataclass


__here__ = pathlib.Path(__file__).resolve().parent


date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


extension_configs = {"toc": {"permalink": " ¶"}}
md = markdown.Markdown(
    extensions=["meta", "toc", "extra"], extension_configs=extension_configs
)


env = jinja2.Environment(loader=jinja2.FileSystemLoader(str(__here__ / "templates")))


# grab yeps --------------------------------------------------------------------------------------


tags = ["meta", "standard", "trait"]


@dataclass
class YEP:
    index: int
    title: str
    authors: [str]
    status: str
    tags: [str]
    post_history: [str]
    content: str

    @property
    def metadata(self) -> str:
        out = "<table>\n"
        out += f"<tr><th>YEP:</th><td>{self.index}</td></tr>\n"
        out += f"<tr><th>Title:</th><td>{self.title}</td></tr>\n"
        out += f"<tr><th>Authors:</th><td>{', '.join(self.authors)}</td></tr>\n"
        out += f"<tr><th>Status:</th><td>{self.status}</td></tr>\n"
        out += f"<tr><th>Tags:</th><td>{', '.join(self.tags)}</td></tr>\n"
        out += f"<tr><th>Post-History:</th><td>{', '.join(self.post_history)}</td></tr>\n"
        out += "</table>\n"
        return out


yeps = []
for yep in os.listdir(__here__ / "yeps"):
    with open(__here__ / "yeps" / yep, "r") as f:
        s = f.read()
        content = md.convert(s)
        kwargs = dict()
        kwargs["index"] = int(md.Meta["yep"][0])
        kwargs["title"] = md.Meta["title"][0]
        kwargs["authors"] = md.Meta["author"]
        kwargs["status"] = md.Meta["status"][0]
        kwargs["tags"] = md.Meta["tags"]
        kwargs["post_history"] = md.Meta["post-history"]
        kwargs["content"] = content
        for t in kwargs["tags"]:
            assert t in tags
        yeps.append(YEP(**kwargs))


yeps.sort(key=lambda y: y.index)

# index -------------------------------------------------------------------------------------------


if not os.path.isdir(__here__ / "public"):
    os.mkdir(__here__ / "public")


template = env.get_template("index.html")
with open(__here__ / "public" / "index.html", "w") as f:
    f.write(template.render(yeps=yeps, title="yaq enhancement proposals", date=date))


# YEP-0 -------------------------------------------------------------------------------------------


if not os.path.isdir(__here__ / "public" / "000"):
    os.mkdir(__here__ / "public" / "000")


template = env.get_template("yep0.html")
with open(__here__ / "public" / "000" / "index.html", "w") as f:
    f.write(
        template.render(
            yeps=yeps,
            title="yaq enhancement proposals",
            date=date,
            tags=tags,
        )
    )


# posts -------------------------------------------------------------------------------------------


template = env.get_template("yep.html")
for yep in yeps:
    if not os.path.isdir(__here__ / "public" / str(yep.index).zfill(3)):
        os.mkdir(__here__ / "public" / str(yep.index).zfill(3))
    with open(__here__ / "public" / str(yep.index).zfill(3) / "index.html", "w") as f:
        f.write(template.render(yep=yep, title=yep.title, date=date))


# css ---------------------------------------------------------------------------------------------


template = env.get_template("style.css")
for d, _, _ in os.walk(__here__ / "public", topdown=False):
    with open(os.path.join(d, "style.css"), "w") as f:
        f.write(template.render())
