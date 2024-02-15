import networkx as nx
import matplotlib.pyplot as plt

def generate_connectivity_graph(nodeArray):
    G = nx.Graph()
    for node in nodeArray: #iterating over the all noe object from the nodeArray list of nodes 
        # G.add_node(node.nodeID, label=f"Node {node.nodeID}, Hashpower: {node.hashPower}")  # we can adjust attributes which to display
        G.add_node(node.nodeID, label=f"{node.nodeID}")
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
    # plt.savefig("Results/GraphOfNodes/node_connectivity_graph_of_N_Nodes.png")
    plt.savefig("node_connectivity_graph.png")

    # To Show the graph
    plt.show(block=False)


def generate_blockchain_graph_of_one_node(node):
    G = nx.Graph()
    #  we extract the following from the node
    # blockSeen is dictionary of node which has {hash of block , object of blocks} 
    #  leafblock is disctionary of leafs node hash {hash of block , object of block}
    blockSeen = node.blockSeen
    leafBlocks = node.leafBlocks
    # for every leaf to genesis block generate a edge connected graph 
    for leaf in leafBlocks.keys():
        #  for every leaf traverse from leaf till gnesis block
        currBlock = blockSeen.get(leaf)
        # looping from one leaf to till i get a get a genesis block and creating edges between all of them 
        while not currBlock.isGenesis:
            parentHash = currBlock.previousBlock
            parentBlock = blockSeen.get(parentHash)
            # Creating edges between current block and its parent block
            G.add_node(currBlock.blockHash, label=f"{currBlock.blockHash}")
            G.add_edge(currBlock.blockHash, parentBlock.blockHash)
            currBlock = parentBlock

    return G

def generate_blockchain_graph_visualization(nodeArray):

    #  here node array contains object of all nodes we will take nodes one by one an inside the node we have 
    #  one blockchain each and for each blockchain we will generate a visualization 
    for node in nodeArray:    
        # Generate the blockchain connectivity graph
        blockchain_graph = generate_blockchain_graph_of_one_node(node)

        # Drawing the graph of blockchain on node i 
        node_labels = nx.get_node_attributes(blockchain_graph, 'label')
        nx.draw(blockchain_graph, with_labels=True,labels=node_labels, node_size=1000, node_color="skyblue", font_size=12, font_weight="bold")
        plt.title("Block Chain of Node "+node.nodeID)

        # Saving the graph as an image file in Results/Blockchains
        # plt.savefig("Results/GraphOfNodes/node_connectivity_graph_of_N_Nodes.png")
        filename = "Results/BlockChains/blockchain_graph_of_node_"+node.nodeID+".png"
        plt.savefig(filename)

        # To Show the graph
        # plt.show()
    return
