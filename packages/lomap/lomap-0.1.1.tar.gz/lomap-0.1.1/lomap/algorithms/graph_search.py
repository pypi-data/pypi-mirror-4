import networkx as nx
import logging
from collections import defaultdict

# Logger configuration
logger = logging.getLogger(__name__)
#logger.addHandler(logging.NullHandler())

__all__ = ['bfs_edges', 'dfs_edges', 'bfs_successors', 'dfs_successors', 'is_reachable_bfs', 'is_reachable_dfs']

def bfs_edges(G,source,degen_paths=False):
	"""
	Produce edges in a breadth-first-search starting at source.

	Adapted from networkx.algorithms.traversal.breadth_first_search.bfs_edges
	to support non-degenerate paths.
	"""
	if degen_paths:
		visited=set([source])
	else:
		visited=set([])
	stack = [(source,iter(G[source]))]
	while stack:
		parent,children = stack[0]
		try:
			child = next(children)
			if child not in visited:
				yield parent,child
				visited.add(child)
				stack.append((child,iter(G[child])))
		except StopIteration:
			stack.pop(0)

def dfs_edges(G,source,degen_paths=False):
	"""
	Produce edges in a depth-first-search starting at source.

	Adapted from networkx.algorithms.traversal.depth_first_search.dfs_edges
	to support non-degenerate paths.
	"""
	nodes=[source]
	visited=set()
	for start in nodes:
		if start in visited:
			continue
		if degen_paths:
			visited.add(start)
		stack = [(start,iter(G[start]))]
		while stack:
			parent,children = stack[-1]
			try:
				child = next(children)
				if child not in visited:
					yield parent,child
					visited.add(child)
					stack.append((child,iter(G[child])))
			except StopIteration:
				stack.pop()

def bfs_successors(G, source):
	"""
	Return dictionary of successors in breadth-first-search from source.

	Taken from networkx.algorithms.traversal.breadth_first_search.
	"""
	d=defaultdict(list)
	for s,t in bfs_edges(G,source):
		d[s].append(t)
	return dict(d)

def dfs_successors(G, source):
	"""
	Return dictionary of successors in depth-first-search from source.

	Taken from networkx.algorithms.traversal.depth_first_search.
	"""
	d=defaultdict(list)
	for s,t in dfs_edges(G,source):
		d[s].append(t)
	return dict(d)

def is_reachable_dfs(G, source, target):
	"""
	Checks if target is reachable from the source using
	depth-first-search from the source.
	"""
	for _,t in dfs_edges(G,source):
		if t == target:
			return True
	return False

def is_reachable_bfs(G, source, target):
	"""
	Checks if target is reachable from the source using
	breadth-first-search from the source.
	"""
	for _,t in bfs_edges(G,source):
		if t == target:
			return True
	return False
