import networkx as nx
import re
import itertools
from model import Model

class Ts(Model):
   """
   Base class for (weighted) transition systems.
   """

   def read_from_file(self, path): 
       """
       Reads a LOMAP Ts object from a given file
       """

       # Open and read the file
       # NOTE: File *must* end with an endline character
       with open(path, 'r') as f:
           lines = f.readlines()
           lines = [line.strip() for line in lines]
       line_cnt = 0;

       ## Part-1: Model attributes

       # Name of the model
       m = re.search('name (.*$)', lines[line_cnt])
       self.name = m.group(1)
       line_cnt += 1

       # Initial distribution of the model
       m = re.search('init (.*$)', lines[line_cnt])
       self.init = eval(m.group(1))
       line_cnt += 1

       # End of part-1
       if(lines[line_cnt] != ';'):
           raise Exception("Line %d: Exptected ';', read '%s'!" % (line_cnt, lines[line_cnt]))
       line_cnt += 1

       ## Part-2: State attributes
       state_attr = dict();
       while(line_cnt < len(lines) and lines[line_cnt] != ';'):
           m = re.search('(\S*) (.*)$', lines[line_cnt]);
           exec("state_attr['%s'] = %s" % (m.group(1),m.group(2)));
           line_cnt += 1
       line_cnt+=1

       ## Part-3: Edge list with attributes
       self.g = nx.parse_edgelist(lines[line_cnt:-1], comments='#', create_using=nx.MultiDiGraph())

       # Add state attributes to nodes of the graph
       for node in state_attr.keys():
           for key in state_attr[node].keys():
               # Copy defined attributes to the node in the graph
               self.g.node[node][key] = state_attr[node][key]
               # Define custom node label
               # TODO: label keeps last attribute, fix this
               self.g.node[node]['label'] = '%s\\n%s' % (node, list(state_attr[node][key]))

   def controls_from_run(self, run):
       a = run[0:-1]
       b = run[1:]
       controls = [];
       for source, target in zip(a,b):
           for edge in self.g[source][target].values():
               controls.append(edge['control'])

       return controls

   def next_states_of_wts(self, q, traveling_states = True):
       """
       Returns a tuple (next_state, remaining_time) for each outgoing transition from q in a tuple.

       Parameters:
       -----------
       q : Node label or a tuple
           A tuple stands for traveling states of the form (q,q',x), i.e. robot left q x time units
           ago and going towards q'.

       Notes:
       ------
       1) The tuple option *does not* work on team transition systems where node labels are already
           tuples.
       """
       if(traveling_states and type(q) == tuple):
           # the last[0] is required because MultiDiGraph edges have keys
           return ((q[1], self.g[q[0]][q[1]][0]['weight']-q[2], self.g[q[0]][q[1]][0]['control']),)
       else:
           return tuple(map(lambda e: (e[1], self.g[e[0]][e[1]][0]['weight'], self.g[e[0]][e[1]][0].get('control','')), nx.edges_iter(self.g, q)))
