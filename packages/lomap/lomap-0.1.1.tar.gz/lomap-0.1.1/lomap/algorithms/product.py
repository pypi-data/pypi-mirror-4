import networkx as nx
import itertools
from ..classes.model import Model
from ..classes.ts import Ts
import sys
import logging

# Logger configuration
logger = logging.getLogger(__name__)
#logger.addHandler(logging.NullHandler())

__all__ = ['ts_times_ts', 'ts_times_buchi']

def ts_times_buchi(ts, buchi):

	# Create the product_model
	product_model = Model()

	# Iterate over initial states of the TS
	init_states = []
	for init_ts in ts.init.keys():
		init_prop = ts.g.node[init_ts].get('prop',set())
		# Iterate over the initial states of the FSA
		for init_buchi in buchi.init.keys():
			# Add the initial states to the graph and mark them as initial
			for act_init_buchi in buchi.next_states_of_buchi(init_buchi, init_prop):
				init_state = (init_ts, act_init_buchi)
				init_states.append(init_state)
				product_model.init[init_state] = 1
				product_model.g.add_node(init_state, {'prop':init_prop, 'label':"%s\\n%s" % (init_state,list(init_prop))})
				if act_init_buchi in buchi.final:
					product_model.final.add(init_state)

	# Add all initial states to the stack
	stack = []
	for init_state in init_states:
		stack.append(init_state)

	# Consume the stack
	while(stack):
		current_state = stack.pop()
		ts_state = current_state[0]
		buchi_state = current_state[1]
	
		for ts_next in ts.next_states_of_wts(ts_state, traveling_states = False):
			ts_next_state = ts_next[0]
			ts_next_prop = ts.g.node[ts_next_state].get('prop',set())
			weight = ts_next[1]
			control = ts_next[2]
			for buchi_next_state in buchi.next_states_of_buchi(buchi_state, ts_next_prop):
				next_state = (ts_next_state, buchi_next_state)
				#print "%s -%d-> %s" % (current_state, weight, next_state)
	
				if(next_state not in product_model.g):
					 next_prop = ts.g.node[ts_next_state].get('prop',set())
	
					 # Add the new state
					 product_model.g.add_node(next_state, {'prop': next_prop, 'label': "%s\\n%s" % (next_state, list(next_prop))})
	
					 # Add transition w/ weight
					 product_model.g.add_edge(current_state, next_state, 0, {'weight':weight, 'control':control})
	
					 # Mark as final if final in buchi
					 if buchi_next_state in buchi.final:
						 product_model.final.add(next_state)
	
					 # Continue search from next state
					 stack.append(next_state)
	
				elif(next_state not in product_model.g[current_state]):
					product_model.g.add_edge(current_state, next_state, 0, {'weight':weight, 'control':control})

	return product_model

def ts_times_ts(ts_tuple):

	# Initial state label is the tuple of initial states' labels
	# NOTE: We assume deterministic TS (that's why we pick [0])
	assert all(map(lambda ts: True if len(ts.init) == 1 else False, ts_tuple))
	init_state = tuple(map(lambda ts: ts.init.keys()[0], ts_tuple))
	product_ts = Ts()
	product_ts.init[init_state] = 1

	# Props satisfied at init_state is the union of props
	# For each ts, get the prop of init state or empty set
	init_prop = map(lambda ts: ts.g.node[ts.init.keys()[0]].get('prop',set()), ts_tuple)

	# This makes each set in the list a new argument and takes the union
	init_prop = set.union(*init_prop)

	# Finally, add the state
	product_ts.g.add_node(init_state, {'prop':init_prop, 'label':"%s\\n%s" % (init_state,list(init_prop))})

	# Start depth first search from the initial state
	stack=[]
	stack.append(init_state)

	while(stack):
		current_state = stack.pop()
		# Actual source states of traveling states
		source_state = tuple(map(lambda q: q[0] if type(q) == tuple else q, current_state))
		# Time spent since actual source states
		time_spent = tuple(map(lambda q: q[2] if type(q) == tuple else 0, current_state))

		# Iterate over all possible transitions
		for tran_tuple in itertools.product(*map(lambda t,q: t.next_states_of_wts(q), ts_tuple, current_state)):
			# tran_tuple is a tuple of m-tuples (m: size of ts_tuple)

			# First element of each tuple: next_state
			# Second element of each tuple: time_left
			next_state = tuple([t[0] for t in tran_tuple])
			time_left = tuple([t[1] for t in tran_tuple])
			control = tuple([t[2] for t in tran_tuple])

			# Min time until next transition
			w_min = min(time_left)

			# Next state label. Singleton if transition taken, tuple if traveling state
			next_state = tuple(map(lambda ss, ns, tl, ts: (ss,ns,w_min+ts) if w_min < tl else ns, source_state, next_state, time_left, time_spent))

			ts1 = ts_tuple[0]
			ts2 = ts_tuple[1]

			# Add node if new
			if(next_state not in product_ts.g):
				 # Props satisfied at next_state is the union of props
				 # For each ts, get the prop of next state or empty set
				 # Note: we use .get(ns, {}) as this might be a travelling state
				 next_prop = map(lambda ts,ns: ts.g.node.get(ns,{}).get('prop',set()), ts_tuple, next_state)
				 next_prop = set.union(*next_prop)

				 # Add the new state
				 product_ts.g.add_node(next_state, {'prop': next_prop, 'label': "%s\\n%s" % (next_state, list(next_prop))})

				 # Add transition w/ weight
				 product_ts.g.add_edge(current_state, next_state, 0, {'weight':w_min, 'control':control})
				 #print "%s -%d-> %s (%s)" % (current_state,w_min,next_state,next_prop)
				 # Continue dfs from ns
				 stack.append(next_state)

			# Add tran w/ weight if new
			elif(next_state not in product_ts.g[current_state]):
				 product_ts.g.add_edge(current_state, next_state, 0, {'weight':w_min, 'control':control})
				 #print "%s -%d-> %s" % (current_state,w_min,next_state)

	# Return ts_1 x ts_2 x ...
	return product_ts
