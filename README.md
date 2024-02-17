# P2P-Network

# To install the requirements:
```bash
pip install -r requirements.txt
```
# To install graphviz binaries in Ubuntu:
```bash
sudo apt install graphviz
```
# To install graphviz binaries in Windows (Add the binaries to the PATH):
```bash
winget install graphviz
```
# To run the simulator:
```bash
python3 main.py node z0 z1 T_Tx I maxEventLoop

# node: Number of Nodes
# z0: Value of z0 (0 < z0 < 1)
# z1: Value of z1 (0< z1 < 1)
# T_Tx: Value of T_Tx
# I: Value of I
# maxEventLoop: Number of times the event loop should run
```

# Results
View results in ./Results:\
BlockChains ==> Block Tree Diagrams for each node in PDF and PNG format\
GraphOfNodes ==> Peer graph\
Records ==> Records about each node in HTML and TXT format