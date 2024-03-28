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

def generate_node_connectivity_graph(nodeArray, colors):
    # Generate the connectivity graph
    connectivity_graph = generate_connectivity_graph(nodeArray)

    node_colors = ["skyblue"]*(len(nodeArray))
    node_colors[-2] = colors[0]
    node_colors[-1] = colors[1]

    # Drawing the graph
    node_labels = nx.get_node_attributes(connectivity_graph, 'label')
    nx.draw(connectivity_graph, nodelist=sorted(list(connectivity_graph)), with_labels=True,labels=node_labels, node_size=1000, node_color=node_colors, font_size=12, font_weight="bold")
    plt.title("Node Connectivity Graph")

    # Saving the graph as an image file
    plt.savefig("./Results/GraphOfNodes/node_connectivity_graph_of_N_Nodes.png")
    # plt.savefig("node_connectivity_graph.png")

    # To Show the graph
    # plt.show()


def generate_blockchain_graph_of_one_node(node, colors, N):
    '''
        This function creates Graph of the blocktree maintained in a node/peer
    '''

    def create_blockchain_digraph(adjacency_list):
        """
                Create a directed graph (Digraph) representing a blockchain from an adjacency list.

                Parameters:
                - adjacency_list: A dictionary where keys are block hashes and values are lists of parent block hashes.

                Returns:
                - G: A Digraph object representing the blockchain graph.

                Comments:
                - This function creates a directed graph (Digraph) using the Graphviz library.
                - The graph represents a blockchain where blocks are nodes and edges indicate parent-child relationships between blocks.
                - Each block hash is truncated to display only the first 4 and last 4 characters in the graph.
                - The adjacency list contains information about which blocks are parents of each block.
        """
        G = Digraph(engine="dot",node_attr={'shape':'box'})

        # Add nodes and edges from the adjacency list
        for block_hash, parent_hashes in adjacency_list.items():
            valueToDisplayInGraph = str(block_hash[:4]) + "..."+ str(block_hash[-4:])
            minedBy = node.blocksSeen[block_hash]["Block"].transactions[0].toNode
            if minedBy >= N:
                G.node(block_hash, label=f"{valueToDisplayInGraph}", color=colors[minedBy - N])
            else:    
                G.node(block_hash, label=f"{valueToDisplayInGraph}")
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

    # Define the filenames for saving the PNG and PDF files
    pngfilename = "./Results/BlockChains/PNG/blockchain_graph_of_node_"+str(node.nodeID)
    pdfilename = "./Results/BlockChains/PDF/blockchain_graph_of_node_"+str(node.nodeID)

    # Render and save the blockchain digraph as a PNG image
    blockchain_digraph.render(pngfilename, format='png', cleanup=True)

     # Render and save the blockchain digraph as a PDF document
    blockchain_digraph.render(pdfilename, format='pdf', cleanup=True)

def generate_blockchain_graph_of_one_attack_node(node, colors, N):
    '''
        This function creates Graph of the blocktree maintained in a attack node/peer
    '''

    def create_blockchain_digraph(adjacency_list):
        """
                Create a directed graph (Digraph) representing a blockchain from an adjacency list.

                Parameters:
                - adjacency_list: A dictionary where keys are block hashes and values are lists of parent block hashes.

                Returns:
                - G: A Digraph object representing the blockchain graph.

                Comments:
                - This function creates a directed graph (Digraph) using the Graphviz library.
                - The graph represents a blockchain where blocks are nodes and edges indicate parent-child relationships between blocks.
                - Each block hash is truncated to display only the first 4 and last 4 characters in the graph.
                - The adjacency list contains information about which blocks are parents of each block.
        """
        G = Digraph(engine="dot",node_attr={'shape':'box'})

        # Add nodes and edges from the adjacency list
        for block_hash, parent_hashes in adjacency_list.items():
            valueToDisplayInGraph = str(block_hash[:4]) + "..."+ str(block_hash[-4:])

            minedBy = node.blocksTree[block_hash]["Block"].transactions[0].toNode
            if minedBy >= N:
                G.node(block_hash, label=f"{valueToDisplayInGraph}", color=colors[minedBy - N])
            else:    
                G.node(block_hash, label=f"{valueToDisplayInGraph}")
            
            for parent_hash in parent_hashes:
                G.edge(block_hash, parent_hash)

        # Add private chain too
        for privateBlock in node.privateChain:
            block_hash = privateBlock[1].blockHash
            parent_hash = privateBlock[1].prevBlockHash
            valueToDisplayInGraph = str(block_hash[:4]) + "..."+ str(block_hash[-4:])
            G.node(block_hash, label=f"{valueToDisplayInGraph}", color=colors[node.nodeID - N], style="dashed")
            G.edge(block_hash,parent_hash,style="dashed")

        return G

    adjacency_list = {}

    for blockID in node.blocksTree:
        if(node.blocksTree[blockID]["Block"].isGenesis):
            continue
        adjacency_list[blockID] = [node.blocksTree[blockID]["Block"].prevBlockHash]

    # Create the blockchain digraph
    blockchain_digraph = create_blockchain_digraph(adjacency_list)

    # Visualize the blockchain digraph
    blockchain_digraph.attr(rankdir='RL')

    # Define the filenames for saving the PNG and PDF files
    pngfilename = "./Results/BlockChains/PNG/blockchain_graph_of_attack_node_"+str(node.nodeID)
    pdfilename = "./Results/BlockChains/PDF/blockchain_graph_of_attack_node_"+str(node.nodeID)

    # Render and save the blockchain digraph as a PNG image
    blockchain_digraph.render(pngfilename, format='png', cleanup=True)

     # Render and save the blockchain digraph as a PDF document
    blockchain_digraph.render(pdfilename, format='pdf', cleanup=True)


def generate_blockchain_graph_visualization(nodeArray, colors):
    """
        Generate visualization for blockchain graphs for each node in the nodeArray.

        Parameters:
        - nodeArray: An array containing blockchain node objects.

        Returns:
        - None
    """
    #  here node array contains object of all nodes we will take nodes one by one an inside the node we have 
    #  one blockchain each and for each blockchain we will generate a visualization 
    for node in nodeArray[:-2]:    
        # Generate the blockchain visualization graph
        generate_blockchain_graph_of_one_node(node, colors, len(nodeArray)-2)

    generate_blockchain_graph_of_one_attack_node(nodeArray[-2], colors, len(nodeArray)-2)
    generate_blockchain_graph_of_one_attack_node(nodeArray[-1], colors, len(nodeArray)-2)

def generate_records_of_one_node_txt(node):
    filename = "./Results/Records/txt/InformationOfNode"+str(node.nodeID)+".txt"
    # Open the file in write mode
    with open(filename, 'w') as f:
        f.write("#############################################################################################################################################################\n\n")
    
        # Node Attribute Details

        # nodeID
        f.write("This is information about node of ID=" + str(node.nodeID)+"\n\n") 

        # isSlow
        f.write("Node Categeory:\n")
        if node.isSlow:
            f.write("\tBandwidth: "+ str("Slow Node\n\n"))
        else:
            f.write("\tBandwidth: "+ str("Fast Node\n\n"))
        
        # /hashPower
        f.write("Hashing Power Fraction: "+ str(node.hashPower)+"\n\n")

        # PoWI
        f.write("PoWI: The interarrival time between blocks on average is "+ str(node.PoWI)+" miliseconds\n\n")

        # T_Tx
        f.write("T_Tx: The mean interarrival time between transactions is "+str(node.T_Tx)+" miliseconds\n\n")

        f.write("#############################################################################################################################################################\n\n")
        # Peers Information
        f.write("Peers Information: \n\n")
        f.write("No of Peers Nodes: "+str(len(node.peers))+"\n")
        peers = []
        for peer in node.peers.keys():
            peers.append(peer)
        f.write("Peers are:" +str(peers)+"\n\n")

        f.write("#############################################################################################################################################################\n\n\n")
       
        # Information of Blocks on this node
        f.write("Information of Blocks on this node: \n\n")

        adjacency_list = {}

        for blockID in node.blocksSeen:
            if(node.blocksSeen[blockID]["Block"].isGenesis):
                adjacency_list[blockID] = []
                continue
            adjacency_list[blockID] = [node.blocksSeen[blockID]["Block"].prevBlockHash]

        f.write("No. of Blocks on this node: " + str(len(adjacency_list)) + "\n")
        f.write("Blocks Adjacency List: " + str(adjacency_list) + "\n\n")
        

        f.write("Blocks Details:  \n\n")

        # Write header
        # The "<" alignment specifier in the format string ensures left alignment of each column.
        # The 70, 15, 10, and 10 represent the fixed width for each column. You can adjust these values as needed to ensure proper spacing.
        f.write("{:<75}{:<20}{:<15}{:<15}\n".format("Block Hash", "Timestamp", "Depth", "Is Genesis"))

        maxLengthOfBlockChain = -1
        totalBlocksInNode  =  0
        longestChainLeaf = None
        arrivalTime = None

        # Loop through each block hash in the adjacency list
        for blockHash in adjacency_list.keys():

            # Retrieve the current block from the node's blocksSeen dictionary
            currBlock = node.blocksSeen[blockHash]["Block"]
            arrivalTimeBlock = node.blocksSeen[blockHash]["arrival_time"]

            # Extract block attributes
            timestamp = currBlock.timestamp
            isGenesis = currBlock.isGenesis
            depth = currBlock.depth

            # Write formatted block data to the file
            f.write("{:<75}{:<20}{:<15}{:<15}\n".format(str(blockHash), str(timestamp), str(depth), str(isGenesis)))

            # Update statistics: maxLengthOfBlockChain and totalBlocksInNode
            if maxLengthOfBlockChain < depth or (maxLengthOfBlockChain == depth and arrivalTimeBlock < arrivalTime):
                maxLengthOfBlockChain = depth
                longestChainLeaf = node.blocksSeen[blockHash]["Block"]
                arrivalTime = arrivalTimeBlock
            totalBlocksInNode+=1

        f.write("\n\nTotal Number of Blocks in BlockChain: "+ str(totalBlocksInNode))
        f.write("\n\nTotal Number of Blocks generated by this node in BlockChain: "+ str(node.cntSuccessfulBlocks))
        f.write("\n\nLength of Longest chain: "+ str(maxLengthOfBlockChain + 1))

        currBlock = longestChainLeaf
        cntBlocksInLongestChain = 0

        while(currBlock):
            # If block is not genesis block and coinbase txn is given to current node (this node has created/mined this block)
            if not currBlock.isGenesis and currBlock.transactions[0].toNode == node.nodeID:
                cntBlocksInLongestChain += 1

            currBlock = currBlock.previousBlock
        
        f.write("\n\nNumber of Blocks created by this node in the Longest chain: "+ str(cntBlocksInLongestChain))
        # The ratio of the number of blocks generated by each node in the Longest Chain of the tree to the total number of blocks it generates.
        if node.cntSuccessfulBlocks == 0:
            f.write("\n\nMPU_node_honest (Number of blocks generated by this node in the Longest Chain of the tree/Total Blocks created by this node): 0/0")
        else:
            f.write("\n\nMPU_node_honest (Number of blocks generated by this node in the Longest Chain of the tree/Total Blocks created by this node): "+ str(cntBlocksInLongestChain/node.cntSuccessfulBlocks))

        f.write("\n\nMPU_node_overall (Number of block in the final public main chain/Total number of blocks generated across all the nodes): "+ str((maxLengthOfBlockChain+1)/totalBlocksInNode))

        f.write("\n\n#############################################################################################################################################################\n\n\n")
        
        f.write("Transactions Details:\n\n")

        heardTXNs = node.heardTXNs
        f.write("No. of transactions heard: "+str(len(heardTXNs))+"\n")

        f.write("#############################################################################################################################################################\n\n\n")
        
    print("Information written to  "+filename+"  successfully.")
    return 

def generate_records_of_one_attack_node_txt(node):
    filename = "./Results/Records/txt/InformationOfAttackNode"+str(node.nodeID)+".txt"
    # Open the file in write mode
    with open(filename, 'w') as f:
        f.write("#############################################################################################################################################################\n\n")
    
        # Node Attribute Details

        # nodeID
        f.write("This is information about attack node of ID=" + str(node.nodeID)+"\n\n") 

        # isSlow
        f.write("Attack Node Categeory:\n")
        if node.isSlow:
            f.write("\tBandwidth: "+ str("Slow Node\n\n"))
        else:
            f.write("\tBandwidth: "+ str("Fast Node\n\n"))
        
        # /hashPower
        f.write("Hashing Power Fraction: "+ str(node.hashPower)+"\n\n")

        # PoWI
        f.write("PoWI: The interarrival time between blocks on average is "+ str(node.PoWI)+" miliseconds\n\n")

        # T_Tx
        f.write("T_Tx: The mean interarrival time between transactions is "+str(node.T_Tx)+" miliseconds\n\n")

        f.write("#############################################################################################################################################################\n\n")
        # Peers Information
        f.write("Peers Information: \n\n")
        f.write("No of Peers Nodes: "+str(len(node.peers))+"\n")
        peers = []
        for peer in node.peers.keys():
            peers.append(peer)
        f.write("Peers are:" +str(peers)+"\n\n")

        f.write("#############################################################################################################################################################\n\n\n")
       
        # Information of Blocks on this node
        f.write("Information of Blocks on this node: \n\n")

        adjacency_list = {}

        for blockID in node.blocksTree:
            if(node.blocksTree[blockID]["Block"].isGenesis):
                adjacency_list[blockID] = []
                continue
            adjacency_list[blockID] = [node.blocksTree[blockID]["Block"].prevBlockHash]

        f.write("No. of Public Blocks on this node: " + str(len(adjacency_list)) + "\n")
        f.write("Public Blocks Adjacency List: " + str(adjacency_list) + "\n\n")
        

        f.write("Public Blocks Details:  \n\n")

        # Write header
        # The "<" alignment specifier in the format string ensures left alignment of each column.
        # The 70, 15, 10, and 10 represent the fixed width for each column. You can adjust these values as needed to ensure proper spacing.
        f.write("{:<75}{:<20}{:<15}{:<15}\n".format("Block Hash", "Timestamp", "Depth", "Is Genesis"))

        maxLengthOfBlockChain = -1
        totalBlocksInNode  =  0
        longestChainLeaf = None
        arrivalTime = None

        # Loop through each block hash in the adjacency list
        for blockHash in adjacency_list.keys():

            # Retrieve the current block from the node's blocksSeen dictionary
            currBlock = node.blocksTree[blockHash]["Block"]
            arrivalTimeBlock = node.blocksTree[blockHash]["arrival_time"]

            # Extract block attributes
            timestamp = currBlock.timestamp
            isGenesis = currBlock.isGenesis
            depth = currBlock.depth

            # Write formatted block data to the file
            f.write("{:<75}{:<20}{:<15}{:<15}\n".format(str(blockHash), str(timestamp), str(depth), str(isGenesis)))

            # Update statistics: maxLengthOfBlockChain and totalBlocksInNode
            if maxLengthOfBlockChain < depth or (maxLengthOfBlockChain == depth and arrivalTimeBlock < arrivalTime):
                maxLengthOfBlockChain = depth
                longestChainLeaf = node.blocksTree[blockHash]["Block"]
                arrivalTime = arrivalTimeBlock
            totalBlocksInNode+=1

        if len(node.privateChain) != 0:

            f.write("\n\nPrivate Chain Details:  \n\n")

            # Write header
            # The "<" alignment specifier in the format string ensures left alignment of each column.
            # The 70, 15, 10, and 10 represent the fixed width for each column. You can adjust these values as needed to ensure proper spacing.
            f.write("{:<75}{:<20}{:<15}{:<15}\n".format("Block Hash", "Timestamp", "Depth", "Is Genesis"))

            for privateBlock in node.privateChain:

                currBlock = privateBlock[1]

                # Extract block attributes
                blockHash = currBlock.blockHash
                timestamp = currBlock.timestamp
                isGenesis = currBlock.isGenesis
                depth = currBlock.depth

                # Write formatted block data to the file
                f.write("{:<75}{:<20}{:<15}{:<15}\n".format(str(blockHash), str(timestamp), str(depth), str(isGenesis)))


        f.write("\n\nTotal Number of Public Blocks in BlockChain: "+ str(totalBlocksInNode))
        f.write("\n\nTotal Number of Blocks generated by this attack node in BlockChain (including Private Blocks): "+ str(node.cntSuccessfulBlocks))
        f.write("\n\nLength of Public Longest chain: "+ str(maxLengthOfBlockChain + 1))

        currBlock = longestChainLeaf
        cntBlocksInLongestChain = 0

        while(currBlock):
            # If block is not genesis block and coinbase txn is given to current node (this node has created/mined this block)
            if not currBlock.isGenesis and currBlock.transactions[0].toNode == node.nodeID:
                cntBlocksInLongestChain += 1

            currBlock = currBlock.previousBlock
        
        f.write("\n\nNumber of Public Blocks created by this attack node in the Longest Public chain: "+ str(cntBlocksInLongestChain))
        # The ratio of the number of blocks generated by each node in the Longest Chain of the tree to the total number of blocks it generates.
        if node.cntSuccessfulBlocks == 0:
            f.write("\n\nMPU_node_adv (Number of blocks generated by this adversary node in the Longest Public Chain of the tree/Total number of blocks mined by this adversary overall): 0/0")
        else:
            f.write("\n\nMPU_node_adv (Number of blocks generated by this adversary node in the Longest Public Chain of the tree/Total number of blocks mined by this adversary overall): "+ str(cntBlocksInLongestChain/node.cntSuccessfulBlocks))

        f.write("\n\nMPU_node_overall (Number of block in the final public main chain/Total number of blocks generated across all the nodes): "+ str((maxLengthOfBlockChain+1)/totalBlocksInNode))

        f.write("\n\nThe fraction of the attacker\'s blocks in the main public chain: "+ str(cntBlocksInLongestChain/(maxLengthOfBlockChain+1)))

        f.write("\n\n#############################################################################################################################################################\n\n\n")
        
        f.write("Transactions Details:\n\n")

        heardTXNs = node.heardTXNs
        f.write("No. of transactions heard: "+str(len(heardTXNs))+"\n")

        f.write("#############################################################################################################################################################\n\n\n")
        
    print("Information written to  "+filename+"  successfully.")
    return 


def generate_records_of_one_node_html(node):

    filename = "./Results/Records/HTML/InformationOfNode"+str(node.nodeID)+".html"
    with open(filename, 'w') as f:
        # Write HTML structure
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n<head>\n<title>Node Information Report of Node {}</title>\n".format(node.nodeID))
        # Add CSS styles for formatting
        f.write("<style>\n")
        f.write("body {\nfont-family: Arial, sans-serif;\nbackground-color: #f4f4f4;\nmargin: 0;\npadding: 0;\n}\n")
        f.write("h1, h2, p {\nmargin-bottom: 20px;\n}\n")
        f.write("table {\nwidth: 100%;\nborder-collapse: collapse;\n}\n")
        f.write("th, td {\nborder: 1px solid #ddd;\npadding: 8px;\ntext-align: left;\n}\n")
        f.write("th {\nbackground-color: #f2f2f2;\n}\n")
        f.write("</style>\n")
        f.write("</head>\n<body>\n")
        
        # Write header
        f.write("<h1 style='text-align: center;'>Node Information Report of Node {}</h1>\n".format(node.nodeID))
        # Write node information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Node Attribute Details</h2>\n")
        f.write("<p>This is information about node with ID: <strong>{}</strong></p>\n".format(node.nodeID))
        f.write("<ul>\n")
        f.write("<li>Node Category: <strong>{}</strong></li>\n".format("Slow Node" if node.isSlow else "Fast Node"))
        f.write("<li>Hashing Power Fraction: <strong>{}</strong></li>\n".format(node.hashPower))
        f.write("<li>PoWI: The interarrival time between blocks on average is <strong>{}</strong> milliseconds</li>\n".format(node.PoWI))
        f.write("<li>T_Tx: The mean interarrival time between transactions is <strong>{}</strong> milliseconds</li>\n".format(node.T_Tx))
        f.write("</ul>\n")
        f.write("</div>\n")

        # Write peers information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Peers Information</h2>\n")
        f.write("<p>No of Peer Nodes: <strong>{}</strong></p>\n".format(len(node.peers)))
        f.write("<p>Peers are: <strong>{}</strong></p>\n".format(", ".join(map(str, node.peers.keys()))))

        f.write("</div>\n")

        # Write blocks information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Blocks Information</h2>\n")
        f.write("<p>No. of Blocks on this node: <strong>{}</strong></p>\n".format(len(node.blocksSeen)))
        f.write("<table>\n")
        f.write("<tr><th>Block Hash</th><th>Timestamp</th><th>Depth</th><th>Is Genesis</th></tr>\n")
        totalBlocksInNode = 0
        maxLengthOfBlockChain = -1
        longestChainLeaf = None
        arrivalTime = None
        for blockHash, blockInfo in node.blocksSeen.items():
            f.write("<tr>")
            f.write("<td>{}</td>".format(blockHash))
            f.write("<td>{}</td>".format(blockInfo["Block"].timestamp))
            f.write("<td>{}</td>".format(blockInfo["Block"].depth))
            f.write("<td>{}</td>".format(blockInfo["Block"].isGenesis))
            if maxLengthOfBlockChain < blockInfo["Block"].depth or (maxLengthOfBlockChain == blockInfo["Block"].depth and blockInfo["arrival_time"] < arrivalTime):
                maxLengthOfBlockChain = blockInfo["Block"].depth
                longestChainLeaf = blockInfo["Block"]
                arrivalTime = blockInfo["arrival_time"]
            totalBlocksInNode+=1
            f.write("</tr>\n")
        f.write("</table>\n")
        f.write("</div>\n")

          # Write additional information
        f.write("<div style='background-color: #fff; padding: 20px;'>\n")
        f.write("<h2>Additional Information About Blockchain</h2>\n")
        f.write("<p>Total Number of Blocks in BlockChain: <strong>{}</strong></p>\n".format(totalBlocksInNode))
        f.write("<p>Total Number of Blocks generated by this node in BlockChain: <strong>{}</strong></p>\n".format(node.cntSuccessfulBlocks))
        f.write("<p>Length of Longest chain: <strong>{}</strong></p>\n".format(maxLengthOfBlockChain + 1))
        currBlock = longestChainLeaf
        cntBlocksInLongestChain = 0

        while(currBlock):
            # If block is not genesis block and coinbase txn is given to current node ==> (this node has created/mined this block)
            if not currBlock.isGenesis and currBlock.transactions[0].toNode == node.nodeID:
                cntBlocksInLongestChain += 1

            currBlock = currBlock.previousBlock
        f.write("<p>Number of Blocks created by this node in the Longest chain: <strong>{}</strong></p>\n".format(cntBlocksInLongestChain))
        # The ratio of the number of blocks generated by each node in the Longest Chain of the tree to the total number of blocks it generates.
        if node.cntSuccessfulBlocks == 0:
            f.write("<p>MPU_node_honest (Number of blocks generated by this node in the Longest Chain of the tree/Total Blocks created by this node): <strong>0/0</strong></p>\n")
        else:
            f.write("<p>MPU_node_honest (Number of blocks generated by this node in the Longest Chain of the tree/Total Blocks created by this node): <strong>{}</strong></p>\n".format(str(cntBlocksInLongestChain/node.cntSuccessfulBlocks)))
        
        f.write("<p>MPU_node_overall (Number of block in the final public main chain/Total number of blocks generated across all the nodes): <strong>{}</strong></p>\n".format(str((maxLengthOfBlockChain+1)/totalBlocksInNode)))
        f.write("</div>\n")


        # Write transactions information
        f.write("<div style='background-color: #fff; padding: 20px;'>\n")
        f.write("<h2>Transactions Information</h2>\n")
        f.write("<p>No. of transactions heard: <strong>{}</strong></p>\n".format(len(node.heardTXNs)))
        f.write("</div>\n")

        # Close HTML structure
        f.write("</body>\n</html>")

def generate_records_of_one_attack_node_html(node):

    filename = "./Results/Records/HTML/InformationOfAttackNode"+str(node.nodeID)+".html"
    with open(filename, 'w') as f:
        # Write HTML structure
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n<head>\n<title>Node Information Report of Attack Node {}</title>\n".format(node.nodeID))
        # Add CSS styles for formatting
        f.write("<style>\n")
        f.write("body {\nfont-family: Arial, sans-serif;\nbackground-color: #f4f4f4;\nmargin: 0;\npadding: 0;\n}\n")
        f.write("h1, h2, p {\nmargin-bottom: 20px;\n}\n")
        f.write("table {\nwidth: 100%;\nborder-collapse: collapse;\n}\n")
        f.write("th, td {\nborder: 1px solid #ddd;\npadding: 8px;\ntext-align: left;\n}\n")
        f.write("th {\nbackground-color: #f2f2f2;\n}\n")
        f.write("</style>\n")
        f.write("</head>\n<body>\n")
        
        # Write header
        f.write("<h1 style='text-align: center;'>Node Information Report of Attack Node, NodeID: <strong>{}</strong></h1>\n".format(node.nodeID))
        # Write node information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Attack Node Attribute Details</h2>\n")
        f.write("<p>This is information about attack node with ID: <strong>{}</strong></p>\n".format(node.nodeID))
        f.write("<ul>\n")
        f.write("<li> Attack Node Category: <strong>{}</strong></li>\n".format("Slow Node" if node.isSlow else "Fast Node"))
        f.write("<li>Hashing Power Fraction: <strong>{}</strong></li>\n".format(node.hashPower))
        f.write("<li>PoWI: The interarrival time between blocks on average is <strong>{}</strong> milliseconds</li>\n".format(node.PoWI))
        f.write("<li>T_Tx: The mean interarrival time between transactions is <strong>{}</strong> milliseconds</li>\n".format(node.T_Tx))
        f.write("</ul>\n")
        f.write("</div>\n")

        # Write peers information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Peers Information</h2>\n")
        f.write("<p>No of Peer Nodes: <strong>{}</strong></p>\n".format(len(node.peers)))
        f.write("<p>Peers are: <strong>{}</strong></p>\n".format(", ".join(map(str, node.peers.keys()))))

        f.write("</div>\n")

        # Write blocks information
        f.write("<div style='background-color: #fff; padding: 20px; margin-bottom: 30px;'>\n")
        f.write("<h2>Blocks Information</h2>\n")
        f.write("<p>No. of Public Blocks on this node: <strong>{}</strong></p>\n".format(len(node.blocksTree.keys())))
        f.write("<br><h3> Public Blocks Details</h3>\n")
        f.write("<table>\n")
        f.write("<tr><th>Block Hash</th><th>Timestamp</th><th>Depth</th><th>Is Genesis</th></tr>\n")
        totalBlocksInNode = 0
        maxLengthOfBlockChain = -1
        longestChainLeaf = None
        arrivalTime = None
        for blockHash, blockInfo in node.blocksTree.items():
            f.write("<tr>")
            f.write("<td>{}</td>".format(blockHash))
            f.write("<td>{}</td>".format(blockInfo["Block"].timestamp))
            f.write("<td>{}</td>".format(blockInfo["Block"].depth))
            f.write("<td>{}</td>".format(blockInfo["Block"].isGenesis))
            if maxLengthOfBlockChain < blockInfo["Block"].depth or (maxLengthOfBlockChain == blockInfo["Block"].depth and blockInfo["arrival_time"] < arrivalTime):
                maxLengthOfBlockChain = blockInfo["Block"].depth
                longestChainLeaf = blockInfo["Block"]
                arrivalTime = blockInfo["arrival_time"]
            totalBlocksInNode+=1
            f.write("</tr>\n")
        f.write("</table>\n")
        f.write("<br><h3> Private Chain Details</h3>\n")
        f.write("<table>\n")
        f.write("<tr><th>Block Hash</th><th>Timestamp</th><th>Depth</th><th>Is Genesis</th></tr>\n")
        for privateBlock in node.privateChain:
            currBlock = privateBlock[1]
            f.write("<tr>")
            f.write("<td>{}</td>".format(currBlock.blockHash))
            f.write("<td>{}</td>".format(currBlock.timestamp))
            f.write("<td>{}</td>".format(currBlock.depth))
            f.write("<td>{}</td>".format(currBlock.isGenesis))
            f.write("</tr>\n")
        f.write("</table>\n")
        f.write("</div>\n")

          # Write additional information
        f.write("<div style='background-color: #fff; padding: 20px;'>\n")
        f.write("<h2>Additional Information About Blockchain</h2>\n")
        f.write("<p>Total Number of Public Blocks in BlockChain: <strong>{}</strong></p>\n".format(totalBlocksInNode))
        f.write("<p>Total Number of Blocks generated by this node in BlockChain (including Private Blocks): <strong>{}</strong></p>\n".format(node.cntSuccessfulBlocks))
        f.write("<p>Length of Public Longest chain: <strong>{}</strong></p>\n".format(maxLengthOfBlockChain + 1))
        currBlock = longestChainLeaf
        cntBlocksInLongestChain = 0

        while(currBlock):
            # If block is not genesis block and coinbase txn is given to current node ==> (this node has created/mined this block)
            if not currBlock.isGenesis and currBlock.transactions[0].toNode == node.nodeID:
                cntBlocksInLongestChain += 1

            currBlock = currBlock.previousBlock
        f.write("<p>Number of Public Blocks created by this attack node in the Longest Public chain: <strong>{}</strong></p>\n".format(cntBlocksInLongestChain))
        # The ratio of the number of blocks generated by each node in the Longest Chain of the tree to the total number of blocks it generates.
        if node.cntSuccessfulBlocks == 0:
            f.write("<p>MPU_node_adv (Number of blocks generated by this adversary node in the Longest Public Chain of the tree/Total number of blocks mined by this adversary overall): <strong>0/0</strong></p>\n")
        else:
            f.write("<p>MPU_node_adv (Number of blocks generated by this adversary node in the Longest Public Chain of the tree/Total number of blocks mined by this adversary overall): <strong>{}</strong></p>\n".format(str(cntBlocksInLongestChain/node.cntSuccessfulBlocks)))
        
        f.write("<p>MPU_node_overall (Number of block in the final public main chain/Total number of blocks generated across all the nodes): <strong>{}</strong></p>\n".format(str((maxLengthOfBlockChain+1)/totalBlocksInNode)))
        f.write("<p>The fraction of the attacker\'s blocks in the main public chain: <strong>{}</strong></p>\n".format(str(cntBlocksInLongestChain/(maxLengthOfBlockChain+1))))
        f.write("</div>\n")


        # Write transactions information
        f.write("<div style='background-color: #fff; padding: 20px;'>\n")
        f.write("<h2>Transactions Information</h2>\n")
        f.write("<p>No. of transactions heard: <strong>{}</strong></p>\n".format(len(node.heardTXNs)))
        f.write("</div>\n")

        # Close HTML structure
        f.write("</body>\n</html>")


def generate_records_of_all_nodes(nodeArray):
    """
        Generate records of all nodes in the nodeArray.

        Parameters:
        - nodeArray: An array containing blockchain node objects.

        Returns:
        - None
    """
    # Here we will iterate over nodes one by one and record all its information in a text file
    for node in nodeArray[:-2]:
        print("Recording all information of node "+ str(node.nodeID))
        
        generate_records_of_one_node_html(node)
        generate_records_of_one_node_txt(node)
    
    print("Recording all information of node "+ str(nodeArray[-2].nodeID))
    generate_records_of_one_attack_node_html(nodeArray[-2])
    generate_records_of_one_attack_node_txt(nodeArray[-2])

    print("Recording all information of node "+ str(nodeArray[-1].nodeID))
    generate_records_of_one_attack_node_html(nodeArray[-1])
    generate_records_of_one_attack_node_txt(nodeArray[-1])

    print("Information of all of nodes Recorded!!")
    return