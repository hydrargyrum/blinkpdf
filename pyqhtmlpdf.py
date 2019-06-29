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
    def convert(self, url, dest, cookies):
        page = QWebEnginePage()

        qurl = QUrl(url)
        store = page.profile().cookieStore()
        for name, value in cookies:
            cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
            cookie.setDomain(qurl.host())
            store.setCookie(cookie)

        loop = QEventLoop()
        page.loadFinished.connect(loop.quit)

        page.load(qurl)
        loop.exec_()

        loop = QEventLoop()
        page.pdfPrintingFinished.connect(loop.quit)

        page.printToPdf(os.path.abspath(dest))
        loop.exec_()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--cookie', action='append', default=[])
    parser.add_argument('url')
    parser.add_argument('dest')
    args = parser.parse_args()

    app = App(sys.argv)
    QtWebEngine.initialize()

    cookies = []
    for cookiestr in args.cookie:
        name, _, value = cookiestr.partition('=')
        cookies.append((name, value))

    app.convert(args.url, args.dest, cookies)
