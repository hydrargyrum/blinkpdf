#!/usr/bin/env python3

from argparse import ArgumentParser
import os
import sys

from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtNetwork import QNetworkCookie
from PyQt5.QtWidgets import (
    QApplication,
)
from PyQt5.QtWebEngine import QtWebEngine
from PyQt5.QtCore import (
    QUrl, QEventLoop,
)


class App(QApplication):
    def convert(self, args):
        page = QWebEnginePage()

        qurl = QUrl(args.url)
        store = page.profile().cookieStore()
        for name, value in args.cookies:
            cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
            cookie.setDomain(qurl.host())
            store.setCookie(cookie)

        loop = QEventLoop()
        page.loadFinished.connect(loop.quit)

        page.load(qurl)
        loop.exec_()

        loop = QEventLoop()
        page.pdfPrintingFinished.connect(loop.quit)

        page.printToPdf(os.path.abspath(args.dest))
        loop.exec_()


def parse_cookies(cookiestr):
    name, _, value = cookiestr.partition('=')
    return (name, value)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '--cookie', type=parse_cookies,
        dest='cookies', action='append', default=[],
    )
    parser.add_argument('url')
    parser.add_argument('dest')
    args = parser.parse_args()

    app = App(sys.argv)
    QtWebEngine.initialize()

    app.convert(args)
