__all__ = ['subset_to_subset_dijkstra_path_value', 'source_to_target_dijkstra']

def subset_to_subset_dijkstra_path_value(source_set, G, target_set, combine_fn = 'sum', degen_paths = False, weight_key = 'weight'):
	"""
	Compute the shortest path lengths between two sets of nodes in a weighted graph.
	Adapted from 'single_source_dijkstra_path_length' in NetworkX.

	Parameters
	----------
	G: NetworkX graph

	source_set: Set of node labels
		Starting nodes for paths

	target_set: Set of node labels
		Ending nodes for paths

	combine_fn: Function, optional (default: (lambda a,b: a+b))
		Function used to combine two path values

	degen_paths: Boolean, optional (default: False)
		Controls whether degenerate paths (paths that do not traverse any edges)
		are acceptable.

	weight_key: String, optional (default: 'weight')
		Edge data key corresponding to the edge weight.

	Returns
	-------
	length : dictionary
		Dictionary of dictionaries of shortest lengths keyed by source and target labels.

	Notes
	-----
	Edge weight attributes must be numerical.
	This algorithm is not guaranteed to work if edge weights
	are negative or are floating point numbers
	(overflows and roundoff errors can cause problems). 
	Input is assumed to be a MultiDiGraph with singleton edges.
	"""
	import heapq

	all_dist = {} # dictionary of final distances from source_set to target_set

	if combine_fn == 'sum':
		# Classical dijkstra
	
		for source in source_set:
			dist = {} # dictionary of final distances from source
			fringe=[] # use heapq with (distance,label) tuples 
	
			if degen_paths:
				# Allow degenerate paths
				# Add zero length path from source to source
				seen = {source:0} 
				heapq.heappush(fringe,(0,source))
			else:
				# Don't allow degenerate paths
				# Add all neighbors of source to start the algorithm
				seen = dict()
				for w,edgedict in iter(G[source].items()):
					edgedata = edgedict[0]
					vw_dist = edgedata[weight_key]
					seen[w] = vw_dist
					heapq.heappush(fringe,(vw_dist,w))
	
			while fringe:
				(d,v)=heapq.heappop(fringe)
	
				if v in dist: 
					continue # Already searched this node.
	
				dist[v] = d	# Update distance to this node
	
				for w,edgedict in iter(G[v].items()):
					edgedata = edgedict[0]
					vw_dist = dist[v] + edgedata[weight_key]
					if w in dist:
						if vw_dist < dist[w]:
							raise ValueError('Contradictory paths found:','negative weights?')
					elif w not in seen or vw_dist < seen[w]:
						seen[w] = vw_dist
						heapq.heappush(fringe,(vw_dist,w))
	
			# Remove the entries that we are not interested in 
			for key in dist.keys():
				if key not in target_set:
					dist.pop(key)
	
			# Add inf cost to target nodes not in dist
			for t in target_set:
				if t not in dist.keys():
					dist[t] = float('inf')
	
			# Save the distance info for this source
			all_dist[source] = dist

	elif combine_fn == 'max':
		# Path length is (max edge length, total edge length)
	
		for source in source_set:
			dist = {} # dictionary of final distances from source
			fringe=[] # use heapq with (bot_dist,dist,label) tuples 
	
			if degen_paths:
				# Allow degenerate paths
				# Add zero length path from source to source
				seen = {source:(0,0)} 
				heapq.heappush(fringe,(0,0,source))
			else:
				# Don't allow degenerate paths
				# Add all neighbors of source to start the algorithm
				seen = dict()
				for w,edgedict in iter(G[source].items()):
					edgedata = edgedict[0]
					vw_dist = edgedata[weight_key]
					seen[w] = (vw_dist,vw_dist)
					heapq.heappush(fringe,(vw_dist,vw_dist,w))
	
			while fringe:
				(d_bot,d_sum,v)=heapq.heappop(fringe)
	
				if v in dist: 
					continue # Already searched this node.
	
				dist[v] = (d_bot,d_sum)	# Update distance to this node
	
				for w,edgedict in iter(G[v].items()):
					edgedata = edgedict[0]
					vw_dist_bot = max(dist[v][0],edgedata[weight_key])
					vw_dist_sum = dist[v][1] + edgedata[weight_key]
					if w in dist:
						if vw_dist_bot < dist[w][0]:
							raise ValueError('Contradictory paths found:','negative weights?')
					elif w not in seen or vw_dist_bot < seen[w][0] or (vw_dist_bot == seen[w][0] and vw_dist_sum < seen[w][1]):
						seen[w] = (vw_dist_bot, vw_dist_sum)
						heapq.heappush(fringe,(vw_dist_bot,vw_dist_sum,w))
	
			# Remove the entries that we are not interested in 
			for key in dist.keys():
				if key not in target_set:
					dist.pop(key)
	
			# Add inf cost to target nodes not in dist
			for t in target_set:
				if t not in dist.keys():
					dist[t] = (float('inf'),float('inf'))
	
			# Save the distance info for this source
			all_dist[source] = dist
	else:
		assert(False)

	return all_dist

def source_to_target_dijkstra(G, source, target, combine_fn = 'sum', degen_paths = False, cutoff=None, weight_key='weight'):
	"""
	Compute shortest paths and lengths in a weighted graph G.
	Adapted from 'single_source_dijkstra_path' in NetworkX.

	Parameters
	----------
	G : NetworkX graph

	source : Node label
		Starting node for the path

	target : Node label
		Ending node for the path 

	degen_paths: Boolean, optional (default: False)
		Controls whether degenerate paths (paths that do not traverse any edges)
		are acceptable.

	cutoff : integer or float, optional (default: None)
		Depth to stop the search. Only paths of length <= cutoff are returned.

	weight_key: String, optional (default: 'weight')
		Edge data key corresponding to the edge weight.

	Returns
	-------
	distance,path : Tuple
		Returns a tuple distance and path from source to target.

	Examples
	--------
	>>> G=networkx.path_graph(5)
	>>> length,path=source_to_target_dijkstra(G,0,4)
	>>> print(length)
	4
	>>> path
	[0, 1, 2, 3, 4]

	Notes
	---------
	Edge weight attributes must be numerical.

	Based on the Python cookbook recipe (119466) at 
	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/119466

	This algorithm is not guaranteed to work if edge weights
	are negative or are floating point numbers
	(overflows and roundoff errors can cause problems). 
	"""
	import heapq

	dist = {}	# dictionary of final distances
	fringe=[] # use heapq with (distance,label) tuples 

	if combine_fn == 'sum':
		if degen_paths:
			# Allow degenerate paths
			if source==target: 
				# Terminate immediately if source == target
				return (0, [source])
			else:
				# Add zero length path from source to source
				paths = {source:[source]}	# dictionary of paths
				seen = {source:0} 
				heapq.heappush(fringe,(0,source))
		else:
			# Don't allow degenerate paths
			# Add all neighbors of source to start the algorithm
			paths = dict()
			seen = dict()
			for w,edgedict in iter(G[source].items()):
				edgedata = edgedict[0]
				vw_dist = edgedata[weight_key]
				paths[w] = [source, w]
				seen[w] = vw_dist
				heapq.heappush(fringe,(vw_dist,w))

		while fringe:
			(d,v)=heapq.heappop(fringe)

			if v in dist: 
				continue # already searched this node.

			dist[v] = d	# Update distance to this node
			if v == target: 
				break	# Discovered path to target node

			for w,edgedict in iter(G[v].items()):
				edgedata = edgedict[0]
				vw_dist = dist[v] + edgedata[weight_key]
				if cutoff is not None:
					if vw_dist>cutoff: 
						continue	# Longer than cutoff, ignore this path
				if w in dist:
					if vw_dist < dist[w]:
						raise ValueError('Contradictory paths found:', 'negative weights?')
				elif w not in seen or vw_dist < seen[w]:
					seen[w] = vw_dist
					paths[w] = paths[v]+[w]
					heapq.heappush(fringe,(vw_dist,w))

		# Add inf cost to target if not in dist
		if target not in dist.keys():
			dist[target] = float('inf')
			paths[target] = ['']

		return (dist[target],paths[target])

	elif combine_fn == 'max':

		if degen_paths:
			# Allow degenerate paths
			if source==target: 
				# Terminate immediately if source == target
				return (0, [source])
			else:
				# Add zero length path from source to source
				paths = {source:[source]}	# dictionary of paths
				seen = {source:(0,0)} 
				heapq.heappush(fringe,(0,0,source))
		else:
			# Don't allow degenerate paths
			# Add all neighbors of source to start the algorithm
			paths = dict()
			seen = dict()
			for w,edgedict in iter(G[source].items()):
				edgedata = edgedict[0]
				vw_dist = edgedata[weight_key]
				paths[w] = [source, w]
				seen[w] = (vw_dist, vw_dist)
				heapq.heappush(fringe,(vw_dist,vw_dist,w))

		while fringe:
			(d_bot,d_sum,v)=heapq.heappop(fringe)

			if v in dist: 
				continue # already searched this node.

			dist[v] = (d_bot,d_sum)	# Update distance to this node
			if v == target: 
				break	# Discovered path to target node

			for w,edgedict in iter(G[v].items()):
				edgedata = edgedict[0]
				vw_dist_bot = max(dist[v][0], edgedata[weight_key])
				vw_dist_sum = dist[v][1] + edgedata[weight_key]
				if cutoff is not None:
					if vw_dist_bot>cutoff: 
						continue	# Longer than cutoff, ignore this path
				if w in dist:
					if vw_dist_bot < dist[w][0]:
						raise ValueError('Contradictory paths found:', 'negative weights?')
				elif w not in seen or vw_dist_bot < seen[w][0] or (vw_dist_bot == seen[w][0] and vw_dist_sum < seen[w][1]):
					seen[w] = (vw_dist_bot, vw_dist_sum)
					paths[w] = paths[v]+[w]
					heapq.heappush(fringe,(vw_dist_bot,vw_dist_sum,w))

		# Add inf cost to target if not in dist
		if target not in dist.keys():
			dist[target] = (float('inf'),float('inf'))
			paths[target] = ['']

		return (dist[target][0],paths[target])
	else:
		assert(False)

# Code that can wrapped subset_to_subset_dijkstra for local parallel execution
#def subset_to_subset_dijkstra_path_value_parallel(G, source_set, target_set, combine_fn = (lambda a,b: a+b), degen_paths = False, weight_key = 'weight',chunk_size = 10, process_cnt=4):
#from multiprocessing import Process, Queue, Manager
#import time
#
#	source_list = list(source_set)
#
#	# dispatch processes
#	process_list = []
#	dict_list = []
#	last_cnt = 0
#	total_cnt = len(source_list)
#	while last_cnt < total_cnt:
#		if last_cnt + chunk_size > total_cnt:
#			new_cnt = total_cnt
#		else:
#			new_cnt = last_cnt + chunk_size
#		dict_list.append(Manager().dict())
#		process_list.append(Process(target=subset_to_subset_dijkstra_path_value, args = (G, dict_list[-1], source_list[last_cnt:new_cnt], target_set, combine_fn, degen_paths, weight_key)))
#		last_cnt = new_cnt
#
#	remaining = [pp for pp in process_list]
#	running = set()
#	just_done = set()
#	completed = 0
#	total = len(process_list)
#	logger.info('There are %d jobs in total', total)
#	# Wait until all jobs are done
#	while completed < total:
#		# Spawn new threads as necessary
#		while len(running)<process_cnt and remaining:
#			new_process = remaining.pop(0)
#			running.add(new_process)
#			new_process.start()
#			logger.info('Spawned new process %s', new_process)
#		for running_process in running:
#			# Join if done
#			if not running_process.is_alive():
#				running_process.join()
#				logger.info('Process %s finished', running_process)
#				just_done.add(running_process)
#		# Book-keeping
#		completed = completed + len(just_done)
#		running = running - just_done
#		just_done = set([])
#		time.sleep(.5)
#
#	logger.info('Starting dict merge')
#	complete_dict = dict()
#	for dd in dict_list:
#		complete_dict.update(dd)
#	logger.info('finished dict merge')
#
#	return complete_dict
