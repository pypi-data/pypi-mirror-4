# -*- coding: utf-8 -*-
import codecs
import markdown

if __name__ == '__main__':
    text = codecs.open("basic.md", mode="r", encoding="utf-8").read()
    html = markdown.markdown(text, extensions=['extra', 'codehilite'])
    body = """<html>
    <head>
        <link rel="stylesheet" href="https://d3oaxc4q5k2d6q.cloudfront.net/m/ab8a6712a20a/compressed/css/e421bfdb2059.css" type="text/css" />
        <link rel="stylesheet" href="https://d3oaxc4q5k2d6q.cloudfront.net/m/ab8a6712a20a/compressed/css/3e07fe91b215.css" type="text/css" />
        <style>
            body { margin: 50px; width: 900px; }
            .codehilite {
                padding: 20px;
                margin: 10px;
                border: dashed 1px gray;
                color: light-grey;
            }
        </style>
    </head>
    <body>%s
    </body>
    </html>"""
    codecs.open("basic.html", "w", encoding="utf-8", errors="xmlcharrefreplace").write(body % html)
