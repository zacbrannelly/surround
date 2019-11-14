import argparse
import signal
import tornado

from .visualise_web_app import VisualiseWebApp

def get_visualise_parser():
    """
    Returns the parser that describes the arguments used by the visualiser command line tool.

    :return: the parser
    :rtype: :class:`argparse.ArgumentParser`
    """

    parser = argparse.ArgumentParser(
        description='Visualise the output from a classifier.')

    return parser

def execute_visualise_tool(parser, args, extra_args):
    """
    Execute the visualiser tool using the arguments parsed from the user.

    :param parser: the parser used
    :type: :class:`argparse.ArgumentParser`
    :param args: the arguments parsed from the user
    :type args: :class:`argparse.Namespace`
    """

    app = VisualiseWebApp()
    app.listen(8000)

    # Ensure CTRL+C will close the app
    signal.signal(signal.SIGINT, app.signal_handler)
    tornado.ioloop.PeriodicCallback(app.try_exit, 100).start()

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
