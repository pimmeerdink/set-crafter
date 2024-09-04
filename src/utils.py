from bandcamp_api import Bandcamp

BC = Bandcamp()


def make_tralbum(url):
    print(url)
    if "album" in url:
        res = BC.get_album(url)
    else:
        res = BC.get_track(url)

    if not res:
        breakpoint()
    return res
