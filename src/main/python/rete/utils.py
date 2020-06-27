from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union
from xml.etree import ElementTree
from xml.etree.ElementTree import Element


def parse_xml(content: str) -> List[Tuple['Rule', Dict[Any, Any]]]:
    from rete import Rule

    result = []
    root = ElementTree.fromstring(content)
    for production in root:
        lhs = Rule()
        lhs.extend(parsing(production[0]))
        rhs = production[1].attrib
        result.append((lhs, rhs))

    return result


def parsing(root: Element) -> List[Union['Has', 'Neg', 'Filter', 'Bind', 'Ncc']]:
    from rete import Bind
    from rete import Filter
    from rete import Has
    from rete import Neg
    from rete import Ncc

    result = []
    for item in root:
        if item.tag == 'has':
            result.append(Has(**item.attrib))
        elif item.tag == 'neg':
            result.append(Neg(**item.attrib))
        elif item.tag == 'filter':
            result.append(Filter(item.text))
        elif item.tag == 'bind':
            to = item.attrib.get('to')
            result.append(Bind(item.text, to))
        elif item.tag == 'ncc':
            n = Ncc()
            n.extend(parsing(item))
            result.append(n)

    return result


def is_var(name: str) -> bool:
    return name.startswith('$')
