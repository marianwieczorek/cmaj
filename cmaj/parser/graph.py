from typing import List

from cmaj.parser.closure import Closure, RuleState
from cmaj.parser.grammar import Grammar


class ClosureGraph(object):
    def __init__(self) -> None:
        from typing import Dict
        from cmaj.utils.ordered_set import OrderedSet
        self._closures: OrderedSet[Closure] = OrderedSet()
        self._successors: List[Dict[str, int]] = []

    @property
    def closures(self) -> List[Closure]:
        return list(self._closures)

    @property
    def num_closures(self) -> int:
        return len(self._closures)

    @property
    def num_edges(self) -> int:
        return sum(len(edges) for edges in self._successors)

    def index(self, closure: Closure) -> int:
        return self._closures.index(closure)

    def __contains__(self, closure: Closure) -> bool:
        return closure in self._closures

    def add_closure(self, closure: Closure) -> None:
        if closure not in self:
            self._closures |= {closure}
            self._successors.append({})

    def successor(self, source_index: int, symbol: str) -> int:
        return self._successors[source_index][symbol]

    def add_edge(self, source: Closure, symbol: str, target: Closure) -> None:
        self.add_closure(source)
        self.add_closure(target)

        source_index = self.index(source)
        target_index = self.index(target)

        assert symbol not in self._successors[source_index]
        self._successors[source_index][symbol] = target_index

    def __repr__(self) -> str:
        from cmaj.utils.stringify import stringify
        return stringify(self, use={'closures': [*self._closures]})


def graph_for(grammar: Grammar) -> ClosureGraph:
    from cmaj.parser.closure import closure_for, successors_for
    graph = ClosureGraph()
    fringe = {closure_for(grammar, RuleState.start(grammar))}
    while fringe:
        source = fringe.pop()
        graph.add_closure(source)

        successors = successors_for(grammar, source)
        fringe |= {target for target in successors.values() if target not in graph}
        for symbol, target in successors.items():
            graph.add_edge(source, symbol, target)
    return graph
