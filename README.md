# BlinkPDF is yet another webpage-to-pdf converter

It uses PyQt6 and QtWebEngine (with Blink engine) to do so.

Pass an URL and an output filename, the page will be retrieved and converted
to PDF. Additionally, it can be given custom cookies and headers and also
some javascript code to execute (if needing to perform custom tweaks to
the page).

## Usage

`blinkpdf [--cookie NAME=VALUE] [--header NAME=VALUE] [--run-script JS_SNIPPET] https://pypi.org/project/blinkpdf/ output.pdf`

## Install

[`pip install blinkpdf`](https://pypi.org/project/blinkpdf/)
