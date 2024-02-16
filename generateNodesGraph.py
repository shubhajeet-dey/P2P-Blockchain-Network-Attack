import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from graphviz import Digraph


def generate_connectivity_graph(nodeArray):
    G = nx.DiGraph()
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
    # plt.show()


def generate_blockchain_graph_of_one_node1(node):
    G1 = nx.DiGraph()
    #  we extract the following from the node
    #  leafblock is disctionary of leafs node hash {hash of block , object of block}

    leafBlocks = node.leafBlocks
    # for every leaf to genesis block generate a edge connected graph 

    linear_positions = {}  # Dictionary to store positions of nodes
    x_pos = 0  # Initial x-coordinate
    for leaf in leafBlocks.keys():
        # leaf is hash of Block
        # for every leaf traverse from leaf till genesis block 
        # print("\nLeaf block Hash "+ str(leaf))
        currBlock = leafBlocks.get(leaf)
        # looping from one leaf to till I get a genesis block and creating edges between all of them 
        while currBlock is not None:
            parentBlock = currBlock.previousBlock
            # print("\nCurrBlock Hash "+ str(currBlock.blockHash) )
            G1.add_node(currBlock.blockHash, label=f"{str(currBlock.blockHash)[:4]}")
            linear_positions[currBlock.blockHash] = (x_pos%15, x_pos/15)  # Assign position
            x_pos += 1  # Increment x-coordinate

            if parentBlock is None:
                break
            # G1.add_node(parentBlock.blockHash, label=f"{str(parentBlock.blockHash)[:4]}")
            linear_positions[parentBlock.blockHash] = (x_pos, 0)  # Assign position
            # x_pos += 1  # Increment x-coordinate
            G1.add_edge(currBlock.blockHash, parentBlock.blockHash)
            currBlock = parentBlock

       # Normalize x-coordinates
    num_nodes = len(linear_positions)
    max_x = num_nodes - 1
    for node, pos in linear_positions.items():
        linear_positions[node] = (pos[0] / max_x, pos[1])

    return G1, linear_positions

def generate_blockchain_graph_of_one_node(node):
    '''
        This function creates Graph of the blocktree maintained in a node/peer
    '''

    def create_blockchain_digraph(adjacency_list):
        G = Digraph(engine="dot",node_attr={'shape':'box'})

        # Add nodes and edges from the adjacency list
        for block_hash, parent_hashes in adjacency_list.items():
            G.node(block_hash, label=f"{block_hash}")
            for parent_hash in parent_hashes:
                G.edge(block_hash, parent_hash)

        return G

    adjacency_list = {}

    for blockID in node.blocksSeen:
        if(node.blocksSeen[blockID]["Block"].isGenesis):
            continue
        adjacency_list[blockID] = [node.blocksSeen[blockID]["Block"].prevBlockHash]

    # Create the blockchain digraph
    blockchain_digraph = create_blockchain_digraph(adjacency_list)

    # Visualize the blockchain digraph
    blockchain_digraph.attr(rankdir='RL')
    filename = "./Results/BlockChains/blockchain_graph_of_node_"+str(node.nodeID)
    blockchain_digraph.render(filename, format='png', cleanup=True)



def generate_blockchain_graph_of_one_node2(node): 
    G1 = nx.DiGraph()
    leafBlocks = node.leafBlocks
    
    linear_positions = {}  # Dictionary to store positions of nodes
    x_pos = 0  # Initial x-coordinate

    queue = []
    for leaf in leafBlocks.keys():
        currBlock = leafBlocks.get(leaf)
        queue.append(currBlock)
        
    while len(queue) > 0:
        queue_size = len(queue)
        for i in range(queue_size):
            currBlock = queue[0]
            queue.pop(0)
            parentBlock = currBlock.previousBlock
            
            G1.add_node(currBlock.blockHash, shape='square', label=f"{str(currBlock.blockHash)[:4]}", style='filled')
            linear_positions[currBlock.blockHash] = (x_pos, -i)  # Assign position
            
            if parentBlock is None:
                break
                
            G1.add_edge(currBlock.blockHash, parentBlock.blockHash)
            queue.append(parentBlock)

        x_pos += 1  # Increment x-coordinate

    return G1, linear_positions

def adjust_levels(graph, root_node):
    level = {}
    for node in nx.topological_sort(graph):
        if node == root_node:
            level[node] = 0
        else:
            parent = next(graph.predecessors(node))
            level[node] = level[parent] + 1
    return level

def get_root(node):
    leafBlocks = node.leafBlocks
    hashOfFirstLeaf = list(leafBlocks.keys())[0]
    currBlock = leafBlocks[hashOfFirstLeaf]
     
    while currBlock is not None:
        if currBlock.isGenesis:
            return currBlock
        currBlock = currBlock.previousBlock
    return None

def generate_blockchain_graph_visualization(nodeArray):

    #  here node array contains object of all nodes we will take nodes one by one an inside the node we have 
    #  one blockchain each and for each blockchain we will generate a visualization 
    print("visualietion")
    for node in nodeArray:    
        # Generate the blockchain connectivity graph
        generate_blockchain_graph_of_one_node(node)

        # # Drawing the graph of blockchain on node i and also 
        # # Define positions for the nodes in a linear order
        # node_labels = nx.get_node_attributes(blockchain_graph, 'label')

        # # root_node = get_root(node)  # Specify the last root node visited
        # # if root_node is not None:
        # #     levels = adjust_levels(blockchain_graph, root_node)
        # # else:
        # #     levels = nx.get_node_attributes(blockchain_graph, 'label')
        # plt.figure(figsize=(20, 12))  # Adjust figure size as needed
        # nx.draw(blockchain_graph, pos=linear_positions, with_labels=True,labels=node_labels, node_size=700, node_color="skyblue", font_size=11, arrows=True,arrowstyle="->")
        # plt.title("Block Chain of Node "+str(node.nodeID))

        # # Saving the graph as an image file in Results/Blockchains
        # # plt.savefig("Results/GraphOfNodes/node_connectivity_graph_of_N_Nodes.png")
        # filename = "Results/BlockChains/blockchain_graph_of_node_"+str(node.nodeID)
        # plt.savefig(filename+".png")

        # # Save the graph as a PDF
        # # plt.savefig(filename+".pdf", format="pdf")

        # # To Show the graph
        # # plt.show()
    return
