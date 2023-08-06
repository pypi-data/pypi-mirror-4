# coding=utf-8
from simpleai.search.utils import FifoList, BoundedPriorityQueue
from simpleai.search.models import (SearchNode, SearchNodeHeuristicOrdered,
                                    SearchNodeStarOrdered,
                                    SearchNodeCostOrdered)


def breadth_first(problem, graph_search=False):
    '''
    Breadth first search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result, and
    SearchProblem.is_goal.
    '''
    return _search(problem,
                   FifoList(),
                   graph_search=graph_search)


def depth_first(problem, graph_search=False):
    '''
    Depth first search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result, and
    SearchProblem.is_goal.
    '''
    return _search(problem,
                   [],
                   graph_search=graph_search)


def limited_depth_first(problem, depth_limit, graph_search=False):
    '''
    Limited depth first search.

    Depth_limit is the maximum depth allowed, being depth 0 the initial state.
    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result, and
    SearchProblem.is_goal.
    '''
    return _search(problem,
                   [],
                   graph_search=graph_search,
                   depth_limit=depth_limit)


def iterative_limited_depth_first(problem, graph_search=False):
    '''
    Iterative limited depth first search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result, and
    SearchProblem.is_goal.
    '''
    solution = None
    limit = 0

    while not solution:
        solution = limited_depth_first(problem, limit, graph_search)
        limit += 1

    return solution


def uniform_cost(problem, graph_search=False):
    '''
    Uniform cost search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result,
    SearchProblem.is_goal, and SearchProblem.cost.
    '''
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeCostOrdered,
                   graph_replace_when_better=True)


def greedy(problem, graph_search=False):
    '''
    Greedy search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result,
    SearchProblem.is_goal, SearchProblem.cost, and SearchProblem.heuristic.
    '''
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeHeuristicOrdered,
                   graph_replace_when_better=True)


def astar(problem, graph_search=False):
    '''
    A* search.

    If graph_search=True, will avoid exploring repeated states.
    Requires: SearchProblem.actions, SearchProblem.result,
    SearchProblem.is_goal, SearchProblem.cost, and SearchProblem.heuristic.
    '''
    return _search(problem,
                   BoundedPriorityQueue(),
                   graph_search=graph_search,
                   node_factory=SearchNodeStarOrdered,
                   graph_replace_when_better=True)


def _search(problem, fringe, graph_search=False, depth_limit=None,
            node_factory=SearchNode, graph_replace_when_better=False):
    '''
    Basic search algorithm, base of all the other search algorithms.
    '''
    memory = {}
    initial_node = node_factory(state=problem.initial_state,
                                problem=problem)
    fringe.append(initial_node)
    memory[problem.initial_state] = initial_node

    while fringe:
        node = fringe.pop()
        if problem.is_goal(node.state):
            return node
        if depth_limit is None or node.depth < depth_limit:
            childs = []
            for n in node.expand():
                if graph_search:
                    if n.state not in memory:
                        memory[n.state] = n
                        childs.append(n)
                    elif graph_replace_when_better:
                        other = memory[n.state]
                        if n < other:
                            childs.append(n)
                            if other in fringe:
                                fringe.remove(other)
                else:
                    childs.append(n)

            for n in childs:
                fringe.append(n)
