from networkx import *
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm
from PIL import Image
from PIL import ImageFilter
import sys


# ###################################################### #
# Definitions
# ###################################################### #


if len(sys.argv) < 2:
	print("usage: image(file name) k(positive) gaussian(0/1) allsteps(0/1)")
	exit()
image = sys.argv[1]
k = 300
gaussianfilter = False
showeachstep = False
if len(sys.argv) > 4:
	k = int(sys.argv[2])
	gaussianfilter = bool(int(sys.argv[3]))
	showeachstep = bool(int(sys.argv[4]))
	print(gaussianfilter)

intDiff = 1
G = Graph()
channel = 0
nshape = 's' # shape of nodes when drawn: 'o' circles, 's' squares
nsize = 2500 # divided by image width


# ###################################################### #
# Algorithm functions
# ###################################################### #


def Int(C):
	if len(C) == 1:
		return intDiff
	T = minimum_spanning_tree(G.subgraph(C))
	maxEdge = max(T.edges(), key=lambda e:T[e[0]][e[1]]['weight'])
	return T[maxEdge[0]][maxEdge[1]]['weight']


def Tau(C):
	return k/len(C)


def MInt(C1, C2):
	return min(Int(C1) + Tau(C1), Int(C2) + Tau(C2))


def Dif(C1, C2):
	min = float('inf')
	for v1 in C1:
		if v1 not in G:
			continue
		edges1 = G[v1]
		for v2 in C2:
			if v2 not in edges1:
				continue
			if edges1[v2]['weight'] < min:
				min = edges1[v2]['weight']
	return min


def D(C1, C2):
	return Dif(C1,C2) > MInt(C1,C2)


# ###################################################### #
# Helping functions
# ###################################################### #


def getComponentsIndices(S, e):
	indices = []
	for i,c in enumerate(S):
		if e[0] in c:
			indices.append(i)
		if e[1] in c:
			indices.append(i)
	return indices


def drawComponents(S, mode, extra_edge=None):
	node_colors = [0] * len(G.nodes())
	edge_colors = []
	edges = []

	for i,C in enumerate(S):
		if mode == 'random':
			color = i
		else:
			color = (min((Int(C) + Tau(C)), 255))	# max e MST weight

		for node in C:
			node_colors[node] = color

		sub_g = G.subgraph(C)
		sub_g_edges = sub_g.edges()
		if sub_g_edges != []:
			edges += sub_g_edges
			edge_colors += [color]*len(sub_g_edges)

	map = 'Paired'
	max = len(S)
	shape = nshape
	if mode != 'random':
		map = 'RdYlGn'
		max = 255
		shape = 'o'
	
	draw_networkx_nodes(G, positions, node_color=node_colors, cmap=plt.get_cmap(map), vmin=0 , vmax=max, node_shape=shape, node_size=nsize)
	draw_networkx_edges(G, positions, edgelist=edges, width=2, edge_color=edge_colors, edge_cmap=plt.get_cmap(map), edge_vmin=0 , edge_vmax=max)
	if extra_edge != None:
		draw_networkx_edges(G, positions, edgelist=[extra_edge], width=10, edge_color=[G[extra_edge[0]][extra_edge[1]]['weight']], edge_cmap=plt.get_cmap(map), edge_vmin=0 , edge_vmax=max)


# ###################################################### #
# Graph initialization from image
# ###################################################### #

print("Creating model...")

img = Image.open(image)
if gaussianfilter:
	img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
width, height = img.size
nsize /= width
pixels = img.load()

# create nodes
for i in range(0, width):
	for j in range(0, height):
		G.add_node(i+j*width)

# create edges
for i in range(1, width-1):
	for j in range(1, height):
		n = i+j*width
		w = abs(pixels[i,j][channel] - pixels[i-1,j][channel])
		G.add_edge(n, n-1, weight=w)
		w = abs(pixels[i,j][channel] - pixels[i-1,j-1][channel])
		G.add_edge(n, n-width-1, weight=w)
		w = abs(pixels[i,j][channel] - pixels[i,j-1][channel])
		G.add_edge(n, n-width, weight=w)
		w = abs(pixels[i,j][channel] - pixels[i+1,j-1][channel])
		G.add_edge(n, n-width+1, weight=w)

# create edges for border pixels
# top
for i in range(1, width):
	w = abs(pixels[i,0][channel] - pixels[i-1,0][channel])
	G.add_edge(i, i-1, weight=w)
# left
for j in range(1, height):
	w = abs(pixels[0,j][channel] - pixels[0,j-1][channel])
	G.add_edge(j*width, (j-1)*width, weight=w)
	w = abs(pixels[0,j][channel] - pixels[1,j-1][channel])
	G.add_edge(j*width, (j-1)*width+1, weight=w)
# right
for j in range(1, height):
	w = abs(pixels[width-1,j][channel] - pixels[width-1,j-1][channel])
	G.add_edge(j*width+(width-1), (j-1)*width+(width-1), weight=w)
	w = abs(pixels[width-1,j][channel] - pixels[width-2,j-1][channel])
	G.add_edge(j*width+(width-1), (j-1)*width+(width-2), weight=w)
	w = abs(pixels[width-1,j][channel] - pixels[width-2,j][channel])
	G.add_edge(j*width+(width-1), j*width+(width-2), weight=w)


# ###################################################### #
# Graph drawing
# ###################################################### #


print("Drawing model...")

plt.imshow(img, interpolation='nearest')
positions = dict()
for i in range(0,width):
	for j in range(0,height):
		positions[i+j*width] = [i,j]
colors = []
for e in G.edges():
	colors.append(G[e[0]][e[1]]['weight'])
draw_networkx_nodes(G, positions, node_size=nsize)
draw_networkx_edges(G, positions, width=2, edge_color=colors, edge_cmap=plt.get_cmap('RdYlGn'), edge_vmin=0 , edge_vmax=255)
plt.show()


# ###################################################### #
# Algorithm
# ###################################################### #


print("Running segmentation algorithm...")

S = []
for v in G:
	S.append([v])


i = 1
n = 0
for e in sorted(G.edges(data=True), key = lambda (a,b,att):att['weight']):
	print(str(i)+"/"+str(len(G.edges())))
	i += 1
	c1,c2 = getComponentsIndices(S,e)
	if n > 0:
		n -= 1
	if (showeachstep and c1 != c2 and n==0) or (showeachstep==None and i==len(G.edges())):
		plt.close('all')
		plt.imshow(img, interpolation='nearest')
		drawComponents(S, 'weights', e)
		plt.show(block=False)

		inp = str(raw_input())
		if inp == 'c':
			showeachstep = None
		try:
			n = int(inp)
		except:
			pass

	if c1 == c2 or e[2]['weight'] > MInt(S[c1],S[c2]):
		continue
	else:
		S[c1] += S[c2]
		S.remove(S[c2])


# ###################################################### #
# Components drawing
# ###################################################### #


print("Drawing "+str(len(S))+" segments...")

plt.close('all')
plt.imshow(img, interpolation='nearest')
drawComponents(S, 'random')
plt.show()

