#!/usr/bin/env python3

from argparse import ArgumentParser
from contextlib import contextmanager
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


@contextmanager
def prepare_loop(sig=None):
    loop = QEventLoop()
    if sig is not None:
        sig.connect(loop.quit)

    yield loop

    loop.exec_()


class App(QApplication):
    def convert(self, args):
        page = QWebEnginePage()

        qurl = QUrl(args.url)
        store = page.profile().cookieStore()
        for name, value in args.cookies:
            cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
            cookie.setDomain(qurl.host())
            store.setCookie(cookie)

        with prepare_loop(page.loadFinished):
            page.load(qurl)


        with prepare_loop(page.pdfPrintingFinished):
            page.printToPdf(os.path.abspath(args.dest))


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
