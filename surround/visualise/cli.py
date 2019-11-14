import argparse
import signal
import logging
import webbrowser

import tornado
from .visualise_web_app import VisualiseWebApp

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def get_visualise_parser():
    """
    Returns the parser that describes the arguments used by the visualiser command line tool.

    :return: the parser
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(prog='viz', description='Visualise the output from a classifier.')
    parser.add_argument('-p', '--port', type=int, help="Port number to bind server to (default: 45711)", default=45711)

    return parser

def execute_visualise_tool(parser, args, extra_args):
    """
    Execute the visualiser tool using the arguments parsed from the user.

    :param parser: the parser used
    :type: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    LOGGER.info("Starting visualisation web app...")
    app = VisualiseWebApp()
    app.listen(args.port)

    # Ensure CTRL+C will close the app
    signal.signal(signal.SIGINT, app.signal_handler)
    tornado.ioloop.PeriodicCallback(app.try_exit, 100).start()

    LOGGER.info("Server started at: http://localhost:%i", args.port)
    webbrowser.open("http://localhost:%i" % args.port)

    tornado.ioloop.IOLoop.instance().start()

def main():
    """
    The entry-point used for testing when the tool is being debugged.
    """

    # Get the parser used for this tool
    parser = get_visualise_parser()
    args = parser.parse_args()

    execute_visualise_tool(parser, args, [])

if __name__ == "__main__":
    main()
