from subprocess import call
import sys

if __name__ == '__main__':
    args = ["pserve"]
    if len(sys.argv) > 1:
        config = sys.argv[1] + '.ini'
        args.append(config)
        args.extend(sys.argv[2:])
    else:
        args.append('production.ini')

    call(args)
