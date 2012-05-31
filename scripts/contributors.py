import requests


api = lambda path: 'https://api.github.com' + path


def main(args):
    response = requests.get(api('/repos/gsamokovarov/frames.py/contributors'))

    for metadata in response.json:
        print '%(login)s: %(contributions)d commits' % metadata


if __name__ == '__main__':
    main(__import__('sys').argv)
