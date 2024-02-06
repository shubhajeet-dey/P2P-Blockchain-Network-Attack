import networkx as nx
import matplotlib.pyplot as plt

def generate_connectivity_graph(nodeArray):
    G = nx.Graph()
    for node in nodeArray: #iterating over the all noe object from the nodeArray list of nodes 
        G.add_node(node.nodeID, label=f"Node {node.nodeID}, Hashpower: {node.hashPower}")  # we can adjust attributes which to display
        for peer in node.peers.keys(): #iteratig over the peers list/dictionary of the current node and add edge between these
            G.add_edge(node.nodeID, peer)
    return G

def generate_node_connectivity_graph(nodeArray):
        

    # Generate the connectivity graph
    connectivity_graph = generate_connectivity_graph(nodeArray)

    # Drawing the graph
    node_labels = nx.get_node_attributes(connectivity_graph, 'label')
    nx.draw(connectivity_graph, with_labels=True,labels=node_labels, node_size=1000, node_color="skyblue", font_size=12, font_weight="bold")
    plt.title("Node Connectivity Graph")

    # Saving the graph as an image file
    plt.savefig("node_connectivity_graph.png")

    # To Show the graph
    plt.show()