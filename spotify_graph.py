import os
from os import path
import sys
import json

import pandas as pd
import numpy as np
#import dgl
import networkx as nx
import torch

class SpotifyGraph():

    def __init__(self, dir, features_dir):
        
        self.base_dir = dir
        self.tracks_pth = path.join(dir, "tracks.json")
        self.col_pth = path.join(dir, "collections.json")
        self.graph_pth = path.join(dir, "graph.json")

        self.img_dir = path.join(dir, "images")
        self.clip_dir = path.join(dir, "clips")

        self.ft_dir = features_dir
        self.features_dict = {}

        print("Loading graph...")
        self.load()


    def load(self):
        with open(self.tracks_pth, "r", encoding="utf-8") as f:
            self.tracks = json.load(f)
        with open(self.col_pth, "r", encoding="utf-8") as f:
            self.collections = json.load(f)
        with open(self.graph_pth, "r", encoding="utf-8") as f:
            self.graph = json.load(f)

    def save(self):
        '''Save dataset to load directory.'''
        self.save_as(self.base_dir)

    def save_as(self, dir):
        '''Save dataset to provided directory.'''

        with open(path.join(dir, "tracks.json"), "w", encoding="utf-8") as f:
            json.dump(self.tracks, f, ensure_ascii=False, indent=2)  
        with open(path.join(dir, "collections.json"), "w", encoding="utf-8") as f:
            json.dump(self.collections, f, ensure_ascii=False, indent=2) 
        with open(path.join(dir, "graph.json"), "w", encoding="utf-8") as f:
            json.dump(self.graph, f, ensure_ascii=False, indent=2)

    
    def to_dataframe(self):
        '''Get track metadata, collection metadata and graph asPandas dataframes.'''

        tracks = pd.from_dict()

    # def to_dgl_graph(self):
    #     '''Get dataset as a DGL simple graph.
    #         Nodes with ids [0, len(track_ids)) correspond to tracks.
    #         Nodes with ids [len(track_ids), len(track_ids)+len(col_ids)) correspond to collections.'''

    #     track_ids = list(self.tracks)
    #     col_ids = list(self.collections)
    #     all_ids = track_ids.copy()
    #     all_ids.extend(col_ids)

    #     g = dgl.DGLGraph()
    #     n_nodes = len(track_ids) + len(col_ids)
    #     g.add_nodes(n_nodes)

    #     # vectors of "to" and "from" nodes for all edges
    #     # bidirectional duplicates are included in self.graph["edges"]
    #     index_map = {nid: i for i, nid in enumerate(all_ids)}

    #     from_nodes = [ index_map[e["from"]] for e in self.graph["edges"] ]
    #     to_nodes = [ index_map[e["to"]] for e in self.graph["edges"]]

    #     g.add_edges(from_nodes, to_nodes)
    #     # BUG: why is this a DGLHeterorgraph??

    #     #self.g, self.track_ids, self.col_ids, self.features = g, track_ids, col_ids, features
    #     return g, track_ids, col_ids


    def to_nx_graph(self):
        '''Get dataset as a NetworkX graph.'''
        
        g = nx.Graph()
        g.add_nodes_from(self.graph["collections"], bipartite=0)
        g.add_nodes_from(self.graph["tracks"], bipartite=1) 
        edge_tuples = [ (e["from"], e["to"]) for e in self.graph["edges"] ] 
        g.add_edges_from( edge_tuples )

        track_ids = list(self.tracks)
        col_ids = list(self.collections)

        return g, track_ids, col_ids


    def load_features(self, ids=None, norm=False):
        '''Return node features for nodes with given ids. If None, return for all ids.
        Normalize batch if [norm] is True'''

        if not self.ft_dir:
            raise Exception("Node feature directory not provided.")
        
        batch_features = []
        for node_id in ids:
            batch_features.append( torch.load(
                os.path.join(self.ft_dir, node_id, ".pt")) )

        features = torch.stack(batch_features, dim=0)
        if norm:
            mean = features.mean(dim=0)
            std = features.std(dim=0, unbiased=True) + 1e-12
            features = (features - mean) / std
        
        return features

    def song_metadata_from_index(self, index_id):
        '''Get track metadata for track with dgl graph index [index_id]'''

        track_ids = list(self.tracks)
        metadata = self.tracks[track_ids[index_id]]
        return metadata



if __name__ == "__main__":

    # Example usage of the SpotifyGraph dataset class
    dataset = SpotifyGraph("./dataset", None)
    g, track_ids, col_ids = dataset.to_nx_graph()
    print(g)

