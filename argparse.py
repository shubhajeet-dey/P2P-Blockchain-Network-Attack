#!/usr/bin/env python3

def parseArguments(inputs):

    if len(inputs) != 7:
        print("usage : python3 <filename.py> nodes, z0, z1, T_Tx, I, wrongTxnProb\n")
    else:
        required_input = {
            'nodes'             : inputs[1],
            'z0'                : inputs[2],
            'z1'                : inputs[3],
            'T_Tx'              : inputs[4],
            'I'                 : inputs[5],
            'WrongTxnProb'      : inputs[6]
        }
        return required_input