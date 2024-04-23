from __future__ import annotations
import json
import math
from typing import List

verbose = False

# DO NOT MODIFY!
class Node():
    def  __init__(self,
                  key      : int,
                  value    : str,
                  toplevel : int,
                  pointers : List[Node] = None):
        self.key      = key
        self.value    = value
        self.toplevel = toplevel
        self.pointers = pointers

# DO NOT MODIFY!
class SkipList():
    def  __init__(self,
                  maxlevel : int = None,
                  nodecount: int = None,
                  headnode : Node = None,
                  tailnode : Node = None):
        self.maxlevel = maxlevel
        self.nodecount = nodecount
        self.headnode  = headnode
        self.tailnode  = tailnode

    # DO NOT MODIFY!
    # Return a reasonable-looking json.dumps of the object with indent=2.
    # We create an list of nodes,
    # For each node we show the key, the value, and the list of pointers and the key each points to.
    def dump(self) -> str:
        currentNode = self.headnode
        nodeList = []
        while currentNode is not self.tailnode:
            pointerList = str([n.key for n in currentNode.pointers])
            nodeList.append({'key':currentNode.key,'value':currentNode.value,'pointers':pointerList})
            currentNode = currentNode.pointers[0]
        pointerList = str([None for n in currentNode.pointers])
        nodeList.append({'key':currentNode.key,'value':currentNode.value,'pointers':pointerList})
        return json.dumps(nodeList,indent = 2)

    # DO NOT MODIFY!
    # Creates a pretty rendition of a skip list.
    # It's vertical rather than horizontal in order to manage different lengths more gracefully.
    # This will never be part of a test but you can put "pretty" as a single line in your tracefile
    # to see what the result looks like.
    def pretty(self) -> str:
        currentNode = self.headnode
        longest = 0
        while currentNode != None:
            if len(str(currentNode.key)) > longest:
                longest = len(str(currentNode.key))
            currentNode = currentNode.pointers[0]
        longest = longest + 2
        pretty = ''
        currentNode = self.headnode
        while currentNode != None:
            lineT = 'Key = ' + str(currentNode.key) + ', Value = ' + str(currentNode.value)
            lineB = ''
            for p in currentNode.pointers:
                if p is not None:
                    lineB = lineB + ('('+str(p.key)+')').ljust(longest)
                else:
                    lineB = lineB + ''.ljust(longest)
            pretty = pretty + lineT
            if currentNode != self.tailnode:
                pretty = pretty + "\n"
                pretty = pretty + lineB + "\n"
                pretty = pretty + "\n"
            currentNode = currentNode.pointers[0]
        return(pretty)

    # DO NOT MODIFY!
    # Initialize a skip list.
    # This constructs the headnode and tailnode each with maximum level maxlevel.
    # Headnode has key -inf, and pointers point to tailnode.
    # Tailnode has key inf, and pointers point to None.
    # Both have value None.
    def initialize(self,maxlevel):
        pointers = [None] * (1+maxlevel)
        tailnode = Node(key = float('inf'),value = None,toplevel = maxlevel,pointers = pointers)
        pointers = [tailnode] * (maxlevel+1)
        headnode = Node(key = float('-inf'),value = None, toplevel = maxlevel,pointers = pointers)
        self.headnode = headnode
        self.tailnode = tailnode
        self.maxlevel = maxlevel
        self.nodecount = 0

    # Create and insert a node with the given key, value, and toplevel.
    # The key is guaranteed to not be in the skiplist.
    # Check if we need to rebuild and do so if needed.
    def expected_top_level(self):
        return 1 + math.log(self.nodecount, 2)
    
    def insert(self,key,value,toplevel):
        #print(key)
        new_pointers = [self.tailnode] * (1 + toplevel)
        new_node = Node(key, value, toplevel, new_pointers)
        for level in range(toplevel + 1):
            self.insert_into_level(level, new_node)
        self.nodecount += 1

        # rebuild checking
        expected_top_level = self.expected_top_level()
        if expected_top_level > self.maxlevel:
            self.rebuild()

        # TODO implement rebuild checking and execution
        return
    
    def rebuild(self):
        data = self.get_node_key_values()
        old_maxlevel = self.maxlevel

        self.initialize(old_maxlevel * 2)
        #self.maxlevel = old_maxlevel * 2

        eligibal_indices = list(range(1, len(data) + 1))
        for level in reversed(range(self.maxlevel + 1)):
            stored_nodes = []
            for idx in eligibal_indices:
                if (idx % (2 ** level)) == 0:
                    key, value = data[idx - 1]
                    self.insert(key, value, level)
                else:
                    stored_nodes.append(idx)
            eligibal_indices = stored_nodes
            if len(eligibal_indices) == 0:
                return

    def get_node_key_values(self):
        data = []
        head = self.headnode
        while head:
            data.append((head.key, head.value))
            head = head.pointers[0]
        
        return data[1:-1]

    
    def insert_into_level(self, level, new_node):
        #print("Level:", level)
        head = self.headnode
        prev = None
        old_head = head
        
        while head:
            next_node = head.pointers[level]
            if next_node.key > new_node.key:
                head.pointers[level] = new_node
                new_node.pointers[level] = next_node
                return
            else:
                head = next_node
        return

    # Delete node with the given key.
    # The key is guaranteed to be in the skiplist.
    def delete(self,key):
        for level, pointer in enumerate(self.headnode.pointers):
            self.delete_from_level(level, key)
        self.nodecount -= 1
    
    def delete_from_level(self, level, key):
        head = self.headnode
        prev = None

        while head.pointers[level]:
            next_node = head.pointers[level]
            if next_node.key == key:
                head.pointers[level] = next_node.pointers[level]
                return
            else:
                #prev = head
                head = next_node
    
    def search_level(self, key, level):
        head = self.headnode
        keys = []
        while head.pointers[level]:
            keys.append(head.key)
            if head.key == key:
                keys.append(head.value)
                return keys
            else:
                head = head.pointers[level]
        return []

    # Search for the given key.
    # Construct a list of all the keys in all the nodes visited during the search.
    # Append the value associated to the given key to this list.
    def search(self,key) -> str:
        A = []
        for level in reversed(range(self.maxlevel + 1)):
            A = self.search_level(key, level)
            if len(A) > 0:
                break
        return json.dumps(A,indent = 2)