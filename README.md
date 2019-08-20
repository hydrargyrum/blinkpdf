BlinkPDF is yet another webpage-to-pdf converter.

It uses PyQt5 and QtWebEngine (with Blink engine) to do so.

Pass an URL and an output filename, the page will be retrieved and converted
to PDF. Additionally, it can be given custom cookies and headers and also
some javascript code to execute (if needing to perform custom tweaks to
the page).

Unfortunately, even though BlinkPDF runs headless and quits as soon as PDF
is written, Qt requires having a valid X11 $DISPLAY. If intending to run
BlinkPDF on a completely headless environment, it's best to run it within
an Xvfb server.
