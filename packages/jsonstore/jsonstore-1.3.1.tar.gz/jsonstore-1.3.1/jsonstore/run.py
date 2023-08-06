"""Usage: jsonstore [options] 

Options:
  -h --help                 Show this help message and exit
  -i IP --ip=IP             The ip to listen to [default: 127.0.0.1]
  -p PORT --port=PORT       The port to connect [default: 31415]
  -d FILE --database=FILE   Database file [default: index.db]

"""

def main():
    from docopt import docopt
    from jsonstore.rest import JSONStore
    from werkzeug.serving import run_simple

    arguments = docopt(__doc__)
    app = JSONStore(arguments['--database'])
    run_simple(arguments['--ip'], int(arguments['--port']), app)


if __name__ == '__main__':
    main()
