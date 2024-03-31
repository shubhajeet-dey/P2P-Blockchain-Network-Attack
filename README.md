# P2P-Network-Attack

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
python3 main.py nodes zeta_1 zeta_2 T_Tx I maxEventLoop

# nodes: Number of Honest Nodes
# zeta_1: Hash Power of Advesary 1 (0 < zeta_1 < 1)
# zeta_2: Hash Power of Advesary 2 (0 < zeta_2 < 1)
# T_Tx: Value of T_Tx in milliseconds
# I: Value of I in milliseconds
# maxEventLoop: Number of times the event loop should run
```

# Results
View results in ./Results:\
BlockChains ==> Block Tree Diagrams for each node in PDF and PNG format\
GraphOfNodes ==> Peer graph\
Records ==> Records about each node in HTML and TXT format