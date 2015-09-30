# Image-Segmentation-spanning-trees
Efficient graph-based image segmentation algorithm that finds evidence of a boundary between two regions using a graph-based segmentation of the image, described in a paper by Felzenszwalb and Huttenlocher

In this paper, the authors use a greedy graph algorithm to segment similar parts of a given image. The authors’ main goal was to maintain a level of detail so that the algorithm would yield reliable segmentation results even in more detailed images. The algorithm uses the segmentation yielded from the previous iteration to decide whether to merge certain components, and will repeat once for every edge. The final segmentation is then returned. 

An image is represented with a graph. Each vertex represents a single pixel and its edges are weighted by how dissimilar the connected pixels/vertices are by some measure; a larger edge weight indicates more dissimilarity. Each vertex will be connected to its neighbor pixels (8 in most cases).
The algorithm is very similar to Kruskal’s algorithm for finding minimum spanning trees.

The input is a graph G = (V, E), with n vertices and m edges. The output is a segmentation of V into components S = ( C1,..., Cr).
1. Sort E by non-decreasing weight
2. Start with a segmentation S0, where each vertex vi is in its own component.
3. Repeat for each edge (i,j) in E
4. Let Ci ,Cj the components that contain vertices  vi and  vj, if  Ci ≠  Cj and w(ij) ≤ MInt(Ci ,Cj ) merge components Ci and Cj 
5. Output S

w(ij) is the weight of the edge (i,j)
MInt(C1 , C2) is a function that gives the smallest internal difference of the components.



Where Int(Ci) measures the internal difference within a component and 𝜏(Ci) is a threshold function that gives a number proportional to the size of the component.

 			

The Int() function gives the weight of the maximum weight edge on the minimum spanning tree of the component. We can consider the Int() function more intuitively as a representation of the internal difference of the component by considering it as the maximum weight edge of the set of edges needed to hold the component together.
The 𝜏() function gives the number resulting of diving a constant k by the size of the component. It makes smaller components more likely to merge, even with a low internal difference. The greater the k, the more likely small components are to merge, thus it sets a scale of observation.

To evaluate the value of the algorithm’s output, the authors of the paper defined two concepts: a too coarse segmentation and a too fine segmentation. We can broadly say that a coarser segmentation will have fewer segmentations than a finer segmentation.

A segmentation is too fine if it contains a pair of components Ci and Cj for which there is no evidence for a boundary, meaning that the weight of the minimum weight edge that connects them is lesser or equal than MInt(Ci , Cj ).

A segmentation is too coarse if it contains some component that can be splitted into two components, resulting in a new segmentation that is not too fine.

A segmentation S output by the described algorithm can’t be too fine nor too coarse, because of certain properties of segmentations and the algorithm. A proof can be found in the paper.
