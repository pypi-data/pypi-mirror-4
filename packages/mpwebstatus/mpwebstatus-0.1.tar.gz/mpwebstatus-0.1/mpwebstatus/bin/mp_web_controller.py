#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Multiprocessing web status dashboard.

Usage:
  mp_web_controller.py [--port=<port>] [--nobrowser] [--insecure]
  mp_web_controller.py -h | --help
  mp_web_controller.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --nobrowser   Don't automatically open a browser tab.
  --insecure    Allow outside connections.

"""
from mpwebstatus import app
from docopt import docopt
import threading
import webbrowser


if __name__ == "__main__":
    args = docopt(__doc__, version='Multiprocessing web status 0.1')
    port = int(args.get("--port", False) or 5000)
    host = "0.0.0.0" if args.get("--insecure", False) else "localhost"

    if not args["--nobrowser"]:
        url = "http://127.0.0.1:{}/".format(port)
        threading.Timer(1., lambda: webbrowser.open_new_tab(url)).start()

    app.run(host=host, port=port)
