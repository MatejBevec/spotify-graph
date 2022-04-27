import os
from os import path
import sys
import json
import urllib

from spotify_graph import SpotifyGraph

def download_clips(ds):
    '''Download .mp3 song previews to [dataset_dir]/clips'''

    if not os.path.isdir(ds.clips_dir):
            os.mkdir(ds.clips_dir)

    fnames = os.listdir(ds.clips_dir)
    n = len(ds.tracks)
    in_folder = set()
    for fname in fnames:
        in_folder.add(fname.rsplit('.')[0])

    all = set(ds.tracks)
    to_download = all - in_folder

    print(f"{n - len(to_download)}/{n} already stored, downloading the rest.")
    print("Ctrl + C to exit.")

    for i,track_id in enumerate(to_download):
        try:
            urllib.request.urlretrieve(ds.tracks[track_id]["preview_url"], path.join(ds.clips_dir, track_id + ".mp3"))
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                sys.exit()
            print(e)
        if i%100 == 0:
            print(f"{i}/{len(to_download)}")

    print("Done.")

def download_images(ds, size="small"):
    '''Download album covers to [dataset_dir]/images'''

    if not os.path.isdir(ds.images_dir):
            os.mkdir(ds.images_dir)

    fnames = os.listdir(ds.images_dir)
    in_folder = set()
    for fname in fnames:
        in_folder.add(fname.rsplit('.')[0])

    all = set([ds.tracks[t]["album_id"] for t in ds.tracks])
    to_download = all - in_folder

    urls = {}
    for t in ds.tracks:
        tr = ds.tracks[t]
        if tr["album_id"] in to_download:
            urls[tr["album_id"]] = tr["image_url"] if not size=="small" else tr["image_url_small"]

    print(f"{len(all) - len(to_download)}/{len(all)} already stored, downloading the rest.")
    print("Ctrl + C to exit.")

    for i,image_id in enumerate(urls):
        try:
            urllib.request.urlretrieve(urls[image_id], path.join(ds.images_dir, image_id + ".jpg"))
        except Exception as e:
            if isinstance(e, KeyboardInterrupt):
                sys.exit()
            print(e)
        if i%100 == 0:
            print(f"{i}/{len(to_download)}")
    
    print("Done.")

def filter_dataset_with_graph(dc, g):
    ''' Return new SpotifyDataset, keeping only nodes and edges present in [g].'''

    dc = SpotifyGraph(dc.base_dir, None)

    for t in list(dc.tracks):
        if t not in g:
            del dc.tracks[t]
    for c in list(dc.collections):
        if c not in g:
            del dc.collections[c]
    
    dc.graph["tracks"] = [t for t in dc.graph["tracks"] if t in g]
    dc.graph["collections"] = [c for c in dc.graph["collections"] if c in g]

    kept_e = [e for e in dc.graph["edges"] if (e["from"], e["to"]) in g.edges ]
    dc.graph["edges"] = kept_e

    return dc

def remove_albums(ds, save_dir=None):
    '''Remove all album nodes, keeping only a pure playlist-song graph.
        Save resulting graph to [save_dir] or overwrite current save, if None.'''

    albums = set([c for c in ds.collections if ds.collections[c]["type"] == "album"])
    g, track_ids, col_ids = ds.to_nx_graph()

    for node in list(g.nodes):
        if node in albums:
            g.remove_node(node)
    
    dc = filter_dataset_with_graph(g)

    if save_dir is None:
        dc.save()
    else:
        dc.save_as(save_dir)



if __name__ == "__main__":
    
    dataset = SpotifyGraph("./dataset", None)

    if sys.argv[1] == "download_clips":
        download_clips(dataset)
    if sys.argv[1] == "download_images":
        download_images(dataset)
    if sys.argv[1] == "remove_albums":
        remove_albums(dataset, sys.argv[2])