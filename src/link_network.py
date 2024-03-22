"""
    LinkNetwork(up, down)

`LinkNetwork` consists of two dictionaries, `up` and `down`, which indicate, respectively,
the links flowing into given link (`up[i]`), and the link it flows into (`down[i]`).
In both cases, the value is an array of link indices. An empty `down` list indicates that `i`
flow out of the network (i.e. `i` is the outlet), and an empty `up` list indicates that `i`
is a headwater.
"""

"""
    LinkNetwork(connection_list::Array{T, 1} where T<:Integer)

`connection_list` defines downstream connections: `connection_list[i] == j` means that link `i`
flows into link `j`. If `connection_list[i] == -1`, that means `i` is the outlet.

Return a `LinkNetwork`
"""

class LinkNetwork:
    def __init__(self, connection_list: list[int]):
        self.up = {i: [] for i in range(1, len(connection_list) + 1)}
        self.down = {i: [] for i in range(1, len(connection_list) + 1)}

        for up_node, down_node in enumerate(connection_list, start=1):
            assert isinstance(down_node, int) #Connection list must contain only integers
            if down_node == -1:
                continue
            self.up[down_node].append(up_node)
            self.down[up_node].append(down_node)



#calculate distance (# links) between each link and outlet

def calc_routing_depth(ln: LinkNetwork, root_node: int): #-> dict[int, int]:
    depth = {n: -1 for n in ln.down.keys()}

    step = 0
    cur = {root_node}

    while len(cur) > 0:
        next = set()
        for i in cur:
            if depth[i] == -1:
                depth[i] = step
                next.update(ln.up[i])
        cur = next
        step += 1

    return depth

#list of link indices sorted by depth

def get_routing_order(ln, root_node):
    depth = calc_routing_depth(ln, root_node)
    return sorted(depth.keys(), key=lambda x: depth[x], reverse=True)



#list of links with no upstream source

def get_headwater_links(ln):
    hw_links = [x for x in ln.up.keys() if len(ln.up[x]) == 0]
    return hw_links

