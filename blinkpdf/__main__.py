#!/usr/bin/env python3
# SPDX-License-Identifier: Unlicense

# This is free and unencumbered software released into the public domain.
# For more information, please refer to <http://unlicense.org/>
# or LICENSE file

from argparse import ArgumentParser
from contextlib import contextmanager
import os
import subprocess
import sys

from PyQt6.QtNetwork import QNetworkCookie
from PyQt6.QtWidgets import (
    QApplication,
)
from PyQt6.QtWebEngineCore import (
    QWebEngineHttpRequest, QWebEnginePage, QWebEngineProfile,
)
from PyQt6.QtCore import (
    QUrl, QEventLoop,
)


__all__ = (
    'init',
    'convert',
    'run_main',
    'xvfb_run_main',
)


APP = None


@contextmanager
def prepare_loop(sig=None):
    loop = QEventLoop()
    if sig is not None:
        sig.connect(loop.quit)

    yield loop

    loop.exec()


class HeadlessPage(QWebEnginePage):
    def javaScriptAlert(self, url, msg):
        pass

    def javaScriptConfirm(self, url, msg):
        return False

    def javaScriptPrompt(self, url, msg, default):
        return False, None

    def chooseFiles(self, mode, old, mime):
        return []

    def printToPdfAndReturn(self):
        output = []

        def callback(content):
            output.append(content)
            self.pdfPrintingFinished.emit('', True)

        with prepare_loop(self.pdfPrintingFinished):
            self.printToPdf(callback)

        return output[0]


def convert(args):
    profile = QWebEngineProfile()
    # explicitly pass None 'parent' to use the 2-params ctor
    page = HeadlessPage(profile, None)

    settings = page.settings()
    attributes = settings.WebAttribute
    settings.setAttribute(attributes.JavascriptCanOpenWindows, False)
    settings.setAttribute(attributes.WebGLEnabled, False)
    settings.setAttribute(attributes.AutoLoadIconsForPage, False)
    settings.setAttribute(attributes.ShowScrollBars, False)

    qurl = QUrl(args['url'])
    req = QWebEngineHttpRequest(qurl)

    for name, value in args.get('headers', ()):
        req.setHeader(name.encode('utf-8'), value.encode('utf-8'))

    store = page.profile().cookieStore()
    for name, value in args.get('cookies', ()):
        cookie = QNetworkCookie(name.encode('utf-8'), value.encode('utf-8'))
        cookie.setDomain(qurl.host())
        store.setCookie(cookie)

    with prepare_loop(page.loadFinished):
        page.load(req)

    for js in args.get('run_script', ()):
        with prepare_loop() as loop:
            page.runJavaScript(js, lambda _: loop.quit())

    if args['dest'] != '-':
        with prepare_loop(page.pdfPrintingFinished):
            page.printToPdf(os.path.abspath(args['dest']))
    else:
        sys.stdout.buffer.write(page.printToPdfAndReturn())


def init(create_app=True):
    global APP

    if QApplication.instance() is None and create_app:
        APP = QApplication(["blinkpdf", "--headless"])


def parse_cookies(cookiestr):
    name, _, value = cookiestr.partition('=')
    return (name, value)


def run_main(args, prepend=None):
    cmd = [sys.executable, __file__] + list(args)
    if prepend:
        cmd = list(prepend) + cmd
    return subprocess.check_output(cmd)


def xvfb_run_main(args):
    # put a very small resolution to reduce used memory, because we don't really need it
    # it doesn't influence pdf size
    return run_main(args, ['xvfb-run', '-a', '-s', '-screen 0 2x2x8'])


def main():
    global APP

    parser = ArgumentParser()
    parser.add_argument(
        '--cookie', type=parse_cookies,
        dest='cookies', action='append', default=[],
    )
    parser.add_argument(
        '--header', type=parse_cookies,
        dest='headers', action='append', default=[],
    )
    parser.add_argument('--run-script', action='append', default=[])
    parser.add_argument('url')
    parser.add_argument('dest')
    args = parser.parse_args()

    # render headless (offscreen vs minimal?)
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    # for some reason, it can segfault if using offscreen with a DISPLAY...
    os.environ.pop('DISPLAY', None)

    # XXX add mysterious --headless for Qt versions like 5.11
    APP = QApplication(sys.argv + ['--headless'])
    init()
    convert(vars(args))


if __name__ == '__main__':
    main()
