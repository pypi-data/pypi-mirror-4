from __future__ import print_function


class RankUpdator(object):
    """
    Updates nodes by the size of their subtree. Allows trees employing this to efficiently answer 
        queries such as "what is the k-th item?" and "what is the order of key 'a' in the
        collection?".
        
    Example:
    
    >>> t = SortedSet(['hao', 'jiu', 'mei', 'jian'], updator = RankUpdator)
    >>> t
    SortedSet(['hao', 'jian', 'jiu', 'mei'])
    >>>
    >>> # 'hao' is item no. 0
    >>> t.kth(0)
    'hao'
    >>> t.order('hao')
    0
    >>>
    >>> # 'mei' is item no. 3
    >>> t.kth(3)
    'mei'
    >>> t.order('mei')
    3
    """        

    # Metadata appended to each node.
    class Metadata(object):
        
        # Updates the rank from the ranks of left and right children.            
        def update(self, key, key_fn, l, r):
            self.rank = 1 + (l.rank if l is not None else 0) + (r.rank if r is not None else 0)
            
        def __repr__(self):
            return str(self.rank)            
            
    def kth(self, k):
        """
        :returns: k-th key
        :raises: :py:exc:`IndexError` if k is too small (negative) or too large (exceeds the 
            order of the largest item).
        """
        
        if k < 0 or k >= len(self): 
            raise IndexError(k)
                
        node = self.root
        while True:
            left_rank = 0 if node.left is None else node.left.metadata.rank
            if left_rank == k:
                return node.key
            elif left_rank > k:
                node = node.left
            else:
                node, k = node.right, k - left_rank - 1
                
    def order(self, key):
        """
        :returns: The order of key in the keys of the container.        
        """
    
        node, k = self.root, 0
        while True:
            if node is None:
                raise KeyError(key)
            if node.key_fn(node.key) == node.key_fn(key):
                return k + (0 if node.left is None else node.left.metadata.rank)
            elif node.key_fn(node.key) < node.key_fn(key):
                k += 1 + (0 if node.left is None else node.left.metadata.rank)
                node = node.right
            else:
                node = node.left       

