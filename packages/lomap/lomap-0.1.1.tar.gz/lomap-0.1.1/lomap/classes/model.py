import networkx as nx
import itertools
from ..algorithms.graph_search import dfs_successors
from ..algorithms.graph_search import is_reachable_dfs

class Model:
	"""
	Base class for various system models.
	"""

	def __init__(self):
		"""
		Empty LOMAP Model object constructor
		"""
		self.name = 'Unnamed system model'
		self.init = dict()
		self.final = set()
		self.g = nx.MultiDiGraph()

	def __nodes_w_prop(self, prop):

		nodes_w_prop = set()
		for node,data in self.g.nodes(data=True):
			if prop in data.get('prop',set()):
				nodes_w_prop.add(node)

		return nodes_w_prop

	def nodes_w_prop(self, prop):

		nodes_w_prop = set()
		for node,data in self.g.nodes(data=True):
			for propset in prop:
				if propset <= data.get('prop',set()):
					nodes_w_prop.add(node)
					break

		return nodes_w_prop

	def has_empty_language(self):
		"""
		Checks if the language of the model is empty.

		This runs much faster than running dijkstras from init to final
		states and between final states.
		"""
		finals_to_consider = set()
		for init in self.init.keys():
			# Find all successors of this initial state
			suc = dfs_successors(self.g, init)
			# suc is a dict of lists of states keyed by parent states
			# invert it to get a set of all reachable states from 
			# the init
			suc = set(vv for k,v in suc.iteritems() for vv in v)
			# Only consider those final states that are
			# reachable from the initial states
			for final in self.final:
				if final in suc:
					finals_to_consider.add(final)

		# Check if any final state can reach itself
		for final in finals_to_consider:
			if is_reachable_dfs(self.g, final, final):
				return False
		return True

	def visualize(self):
		"""
		Visualizes a LOMAP system model
		"""
		nx.view_pygraphviz(self.g)
		#nx.view_pygraphviz(self.g, 'weight')
