from os import path
import glob
import subprocess
import tempfile
from datetime import datetime
from codecs import open
from collections import namedtuple
import shutil
import os
import warnings
import sys

import networkx as nx

CLEAR_JAVA_EXTRA_ARGS = ['-XX:+UseConcMarkSweepGC', '-Xmx6g']
ENCODING = 'UTF-8'

POS_SUFF = '.postag'
PARSE_SUFF = '.parse'
TOK_SUFF = '.pos-retag' # for pre-tokenised files

TIKZ_DEP_TEMPLATE = u"""
  \\centering
  \\begin{dependency}[edge unit distance = %0.2fex]
    \\begin{deptext}
%s    \\end{deptext}
%s
  \\end{dependency}
"""


class ClearWrapper(object):
    """Wrapper for clearparser"""
    def __init__(self, parsing_config, pos_tagging_config, dep_model, clearparser_base):
        """Initialize wrapper for a ClearParser instance with the supplied 
        configuration files. Separate files must be supplied for parsing and
        POS-tagging, while the explict `dep_model` is used for parsing. `clearparser_base`
        should point to the base of the clearparser installation."""
        self.parsing_config = parsing_config
        self.pos_tagging_config = pos_tagging_config
        self.dep_model = dep_model
        self.clearparser_base = clearparser_base
    
    def parse_from_directory(self, directory):
        """Parse all the files in the given directory"""
        pos_tagged_dir = directory + '-postagged'
        os.mkdir(pos_tagged_dir)
        post_pos_tagged_dir = directory + '-postagged-post'
        os.mkdir(post_pos_tagged_dir)
        parsed_dir = directory + '-parsed'
        os.mkdir(parsed_dir)
        post_parsed_dir = directory + '-parsed-post'
        os.mkdir(post_parsed_dir)
        self._pos_tag_directory(directory, pos_tagged_dir)
        for fn in glob.glob(path.join(pos_tagged_dir, '*' + POS_SUFF)):
            base = path.basename(fn)
            self.postprocess_pos_tags(fn, path.join(post_pos_tagged_dir, base + '-mod'))
        self._parse_directory(post_pos_tagged_dir, parsed_dir)
        for fn in glob.glob(path.join(parsed_dir, '*' + PARSE_SUFF)):
            base = path.basename(fn)
            self.postprocess_parsed(fn, path.join(post_parsed_dir, base + '-mod'))
        self._normalize_parsed_filenames(directory, parsed_dir)
    
    def _normalize_parsed_filenames(self, directory, parsed_dir):
        """Normalize from the parsed directories so we get the same
        file structure we would get directly from Clearparser"""
        for fstem in os.listdir(directory):
            parse_matches = glob.glob(path.join(parsed_dir, fstem + '*' + PARSE_SUFF))
            assert len(parse_matches) == 1, "Invalid number of parse files found"
            parse_match = parse_matches[0]
            if fstem.endswith(POS_SUFF):
                fstem = fstem[:-len(POS_SUFF)]
            elif fstem.endswith(TOK_SUFF):
                fstem = fstem[:-len(TOK_SUFF)]
            os.rename(parse_match, path.join(directory, fstem + PARSE_SUFF))
    
    def parse_in_bulk(self, sentences, to_graph=False):
        sentences = self.preprocess_raw(sentences)
        pos_tagged_fname = self._pos_tag_sentence_list(sentences)
        modified_pos_tagged_fname = pos_tagged_fname + '-mod'
        self.postprocess_pos_tags(pos_tagged_fname, modified_pos_tagged_fname)
        parsed_fname = self._parse_single_file(modified_pos_tagged_fname)
        modified_parsed_fname = parsed_fname + '-mod'
        self.postprocess_parsed(parsed_fname, modified_parsed_fname)
        raw_outputs = list(self._raw_parser_output_by_sentence(modified_parsed_fname))
        if to_graph:
            return [DependencyGraph.from_clear_parse(raw) for raw in raw_outputs]
        else:
            return raw_outputs
    
    def _raw_parser_output_by_sentence(self, parsed_fname):
        with open(parsed_fname, encoding=ENCODING) as f:
            contents = f.read()
        for raw in contents.rstrip(u'\n').split(u'\n\n'):
            yield raw
    
    def _pos_tag_directory(self, directory, pos_tagged_directory):
        holding_dir_for_pretagged = pos_tagged_directory + '-already'
        os.mkdir(holding_dir_for_pretagged)
        # first put aside any files which are explitcly pre-tagged (detect from suffix) 
        #  so they don't get double-tagged
        self._move_by_suffix(directory, holding_dir_for_pretagged, POS_SUFF) 
        # do POS-tagging of new files:
        self._do_pos_tagging(directory)
        # put them into the dir for POS-tagged files
        self._move_by_suffix(directory, pos_tagged_directory, POS_SUFF)
        # then handle the pre-tagged files - copy into the original dir
        self._copy_by_suffix(holding_dir_for_pretagged, directory, POS_SUFF)
        self._move_by_suffix(holding_dir_for_pretagged, pos_tagged_directory, POS_SUFF)
        os.rmdir(holding_dir_for_pretagged)
        
    def _pos_tag_sentence_list(self, source_sentences):
        raw_fname = self._get_temp_name('raw')
        with open(raw_fname, 'w', encoding=ENCODING) as f:
            for sent in source_sentences:
                f.write(sent + u'\n')
        pos_fname = self._get_temp_name('pos')
        self._do_pos_tagging(raw_fname, pos_fname)
        return pos_fname

    def _parse_single_file(self, pos_tagged_fname):
        parsed_fname = self._get_temp_name('parsed')
        self._do_parsing(pos_tagged_fname, parsed_fname)
        return parsed_fname

    def _parse_directory(self, directory, parsed_directory):
        self._do_parsing(directory)
        self._move_by_suffix(directory, parsed_directory, PARSE_SUFF)

    def _do_pos_tagging(self, raw_fname, pos_fname=None):
        args = self._get_pos_tagging_args(raw_fname, pos_fname)
        subprocess.check_call(args)
    
    def _do_parsing(self, pos_tagged_fname, parsed_fname=None):
        args = self._get_parsing_args(pos_tagged_fname, parsed_fname)
        subprocess.check_call(args)
    
    def preprocess_raw(self, sentences):
        return sentences
    
    def postprocess_pos_tags(self, pos_tagged_fname, postprocessed_fname):
        shutil.copy(pos_tagged_fname, postprocessed_fname)
    
    def postprocess_parsed(self, parsed_fname, postprocessed_fname):
        shutil.copy(parsed_fname, postprocessed_fname)
    
    def _get_classpath(self):
        jar_path_glob = path.join(self.clearparser_base, 'lib', '*.jar')
        return ':'.join(glob.glob(jar_path_glob))
    
    def _get_required_env(self):
        return {'CLASSPATH': self._get_classpath()}
    
    def _get_temp_name(self, kind):
        tempdir = tempfile.gettempdir()
        fstem = 'clearparser.%s.%s' % (
          datetime.now().strftime('%Y%m%d%H%M%S'), 
          kind)
        return path.join(tempdir, fstem)
    
    def _get_base_args(self):
        return ['java', '-cp', self._get_classpath()] + CLEAR_JAVA_EXTRA_ARGS
    
    def _get_pos_tagging_args(self, raw_fname, pos_fname=None):
        """raw_fname can also be a directory, in which case we don't need pos_fname"""
        return self._get_base_args() + [
          'clear.engine.PosPredict', 
          '-c', self.pos_tagging_config,
          '-i', raw_fname, '-o', pos_fname if pos_fname else 'XXX']

    def _get_parsing_args(self, pos_fname, parsed_fname):
        return self._get_base_args() + [
          'clear.engine.DepPredict', 
          '-c', self.parsing_config,
          '-m', self.dep_model,
          '-i', pos_fname, '-o', parsed_fname if parsed_fname else 'XXX']
    
    def _fnames_with_suffix(self, directory, suff):
        fnames = glob.glob(path.join(directory, '*' + suff))
        if not fnames:
            warnings.warn("No files with suffix '%s' found in '%s'" % (suff, directory))
        return fnames

    def _move_by_suffix(self, orig_dir, new_dir, target_suff):
        for fname in self._fnames_with_suffix(orig_dir, target_suff):
            shutil.move(fname, new_dir)
    
    def _copy_by_suffix(self, orig_dir, new_dir, target_suff):
        for fname in self._fnames_with_suffix(orig_dir, target_suff):
            shutil.copy2(fname, new_dir)
    
class DepGraphError(Exception):
    pass

class DepGraphIntegrityError(DepGraphError):
    pass

class MissingDepGraphNodeError(DepGraphError):
    pass

class DependencyGraph(object):
    """A utility class to handle ClearParser dependency graphs 
    and do some very basic graph operations with them.
    """
    
    def __init__(self, non_root_nodes, links, raw_parser_output=None, graph_label=''):
        self.root_node = RootNode()
        self.nodes = [self.root_node] + non_root_nodes
        self.links = links
        self.nodes_by_id = dict((node.id, node) for node in self.nodes)
        self.raw_parser_output = raw_parser_output
        self.graph_label = graph_label
        self._as_networkx = None
        self._as_pgv = None
    
    def top_content_nodes(self):
        root = self.root_node
        root_predecs = self.predecessors_for_label(root, u'ROOT')
        if len(self.as_networkx().predecessors(root)) != len(root_predecs):
            raise DepGraphIntegrityError(
              "Found a non-ROOT link pointing to the root node in graph %r " % 
              self.graph_label)
        return root_predecs
    
    def predecessors_for_label(self, node, label):
        as_nx = self.as_networkx()
        predecs = []
        for predec_node in as_nx.predecessors(node):
            if label is None or as_nx.adj[predec_node][node]['reln'] == label:
                predecs.append(predec_node)
        return predecs
        
    def predecessors(self, node):
        return self.predecessors_for_label(node, None)
    
    def as_networkx(self):
        if not self._as_networkx:
            self._as_networkx = self._get_networkx()
        return self._as_networkx

    def as_pgv(self):
        if not self._as_pgv:
            self._as_pgv = self._get_pgv()
        return self._as_pgv
    
    def _get_networkx(self):
        graph = nx.DiGraph()
        for node in self.nodes:
            graph.add_node(node)
        for link in self.links:
            graph.add_edge(
              self.nodes_by_id[link.from_id], self.nodes_by_id[link.to_id],
              reln=link.label)
        return graph
    
    def _get_pgv(self):
        import pygraphviz as pgv
        graph = pgv.AGraph(directed=True)
        nodes_for_pgv = dict(
          (node.id, u'%s:%s' % (node.id, self.node_brief_repr(node))) 
          for node in self.nodes)
        for node in self.nodes:
            graph.add_node(nodes_for_pgv[node.id])
        for link in self.links:
            graph.add_edge(
              nodes_for_pgv[link.from_id], nodes_for_pgv[link.to_id], 
              label=link.label)
        graph.graph_attr['rankdir'] = 'BT'
        return graph
    
    def node_brief_repr(self, node):
        return node_form_pos(node) if isinstance(node, DepNode) else str(self.graph_label)
    
    def as_tikz_dep_latex(self, std_direction=True, explicit_zero_node=False,
            edge_unit_distance=3.0):
        dep_text = []
        if explicit_zero_node:
            nodes = self.nodes
        else:
            nodes = self.nodes[1:]
        nids = [n.id for n in nodes]
        forms = [getattr(n, 'form', '') for n in nodes]
        lemmas = [getattr(n, 'lemma', '') for n in nodes]
        postags = [getattr(n, 'pos', '') for n in nodes]
        dt_indent = ' ' * 6
        for dt_elem_list in (nids, forms, lemmas, postags):
            dt_elem_list = [e.replace('&', '$\with$') for e in dt_elem_list]
            dep_text.append(
                dt_indent + u' \\& '.join(dt_elem_list) + u'\\\\ \n')
        nids_to_indexes = dict((n.id, idx + 1) for idx, n in enumerate(nodes))
        edges = []
        edge_indent = ' ' * 4
        if not explicit_zero_node:
            for node in self.top_content_nodes():
                edges.append(u'\\deproot{%d}{ROOT}\n' % nids_to_indexes[node.id])
        for link in self.links:
            if link.label == u'ROOT' and not explicit_zero_node:
                continue
            from_idx = nids_to_indexes[link.from_id]
            to_idx = nids_to_indexes[link.to_id]
            if std_direction:
                from_idx, to_idx = to_idx, from_idx
            dist = abs(from_idx - to_idx)
            if dist > 8:
                unit_dist = 0.5 * edge_unit_distance + \
                    (4.0 * edge_unit_distance) / dist
                scaling = '[edge unit distance = %0.3fex]' % unit_dist
            else:
                scaling = ''
            edges.append(u'%s\\depedge%s{%d}{%d}{%s}\n' % 
                (edge_indent, scaling, from_idx, to_idx, link.label))
        return TIKZ_DEP_TEMPLATE % (
            edge_unit_distance, u''.join(dep_text), u''.join(edges))
        
    def draw(self):
        nxgraph = self.as_networkx()
        node_labels = {}
        for node in self.nodes:
            node_labels[node] = self.node_brief_repr(node)
        layout = nx.spring_layout(nxgraph)
        nx.draw_networkx(nxgraph, pos=layout, labels=node_labels)
        nx.draw_networkx_edge_labels(nxgraph, pos=layout)
    
    @classmethod
    def from_clear_parse(cls, raw_parse_data, graph_label=''):
        nodes = []
        links = []
        for node_data in raw_parse_data.split(u'\n'):
            if not node_data:
                continue
            comps = node_data.split(u'\t')
            nid, form, lemma, pos, _, link_to_nid, link_label = comps
            node = DepNode(nid, form, lemma, pos)
            nodes.append(node)
            if link_to_nid:
                link = DepLink(nid, link_to_nid, link_label)
                links.append(link)
        return cls(nodes, links, raw_parse_data, graph_label)
    
    @classmethod
    def from_clear_parse_file(cls, parse_filename, graph_label=''):
        with open(parse_filename, encoding=ENCODING) as f:
            raw_parse = f.read()
        return cls.from_clear_parse(
            raw_parse, graph_label if graph_label else parse_filename)
    
    @classmethod
    def multi_from_clear_parse_file(cls, parse_filename, graph_label=''):
        with open(parse_filename, encoding=ENCODING) as f:
            raw_parses = f.read()
        for raw_parse in raw_parses.split(u'\n\n'):
            yield cls.from_clear_parse(
                raw_parse, graph_label if graph_label else parse_filename)
    
    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__, self.nodes, self.links)

class RootNode(object):
    @property
    def id(self):
        return '0'
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        return self.id == other.id
    
    def __repr__(self):
        return '%s()' % self.__class__.__name__

DepNode = namedtuple('DepNode', ['id', 'form', 'lemma', 'pos'])
DepLink = namedtuple('DepLink', ['from_id', 'to_id', 'label'])

def node_form_pos(node):
    return u'%s/%s' % (node.form, node.pos)

def node_flp(node):
    return u'%s[%s]/%s' % (node.form, node.lemma, node.pos)

def draw_stored_parse_with_pgv(parse_filename, format='pdf', output_filename=''):
    dep_graph = DependencyGraph.from_clear_parse_file(parse_filename)
    graph_as_pgv = dep_graph.as_pgv()
    graph_as_pgv.layout('dot')
    if not output_filename:
        output_filename = "%s.%s" % (parse_filename, format)
    graph_as_pgv.draw(output_filename)
    