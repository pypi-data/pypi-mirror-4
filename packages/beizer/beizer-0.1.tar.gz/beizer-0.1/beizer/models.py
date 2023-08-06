# -*- coding: utf-8 -*-
from .exceptions import MatrixInitError, LoopExcludeError
from .utils import (matrix_is_quadratic, last_column_of_matrix,
                    last_row_of_matrix)


class Transition(object):
    """Transition with probability in which system spend or allocate resource.
    """

    def __init__(self, probability, resource):
        """Initializes transition.

        Keyword arguments:
        probability -- probability of transition to vertex.
        resource -- mathematical expectation of resource which spend or
        allocate in transition to vertex.

        """
        self.probability = probability
        self.resource = resource

    def __repr__(self):
        return "(P={0}, R={1})".format(self.probability, self.resource)

    def __getitem__(self, key):
        if key == 0:
            return self.probability
        elif key == 1:
            return self.resource
        else:
            raise IndexError('key has to be 0 for probability'
                             ' or 1 for resource')

    def __eq__(self, other):
        return (self.probability == other.probability and
                self.resource == other.resource)


class TransitionMatrix(object):
    """Transition matrix."""

    def __init__(self, src_matrix):
        """Initializes transition matrix."""
        if not isinstance(src_matrix, list):
            raise MatrixInitError('expected a list object')
        if not matrix_is_quadratic(src_matrix):
            raise MatrixInitError('matrix has to be quadratic')

        self._matrix = []
        for row_src in src_matrix:
            row_of_transitions = []
            for column_src in row_src:
                transition = self._extract_transition(column_src)
                row_of_transitions.append(transition)

            if check_sum_of_probabilities(row_of_transitions):
                self._matrix.append(row_of_transitions)
            else:
                raise MatrixInitError(
                    'sum of probabilities has to be equal to zero or one',
                    row_of_transitions
                )

    def __repr__(self):
        return repr(self._matrix)

    def _extract_transition(self, obj_with_two_items):
        """Returns transition object extracted from iterable object.

        If object does not contain two items then function returns None.
        """
        try:
            probability, resource = obj_with_two_items
        except TypeError:
            transition = None
        else:
            transition = Transition(probability=probability, resource=resource)
        return transition

    def has_only_source_and_drain(self):
        """Returns True if matrix has got only source and drain."""
        matrix_2x2 = len(self._matrix) == 2
        return matrix_2x2 and not self.loop_exists()

    def loop_exists(self):
        """Returns True if loop exists in transition matrix."""
        return self._index_of_first_loop() is not None

    def exclude_first_loop(self):
        """Excludes loop from transition matrix."""
        row_loop = column_loop = self._index_of_first_loop()
        try:
            loop = self._matrix[row_loop][column_loop]
        except (TypeError, IndexError):
            raise LoopExcludeError('loop does not found')
        # Loop delete.
        self._matrix[row_loop][column_loop] = None
        # Для исключения петли необходимо поделить вероятности передач,
        # которые находятся на одной строке с петлей, на вероятность петли.
        if any(self._matrix[row_loop]):
            for (trans_index, trans) in enumerate(self._matrix[row_loop]):
                if trans is not None:
                    trans_ = transform_trans_while_excluding_loop(trans, loop)
                    self._matrix[row_loop][trans_index] = trans_

    def exclude_last_vertex(self):
        """Excludes last vertex from transition matrix."""
        # Для исключения узла необходимо умножить передачу из последнего
        # столбца на передачу из последней строки. Произведение поместить на
        # пересечении строки и столбца, сложив его с передачей принимающей
        # ячейки. Например, если в последнем столбце две передачи, а в
        # последней строке три передачи, то получим шесть произведений.
        last_column = last_column_of_matrix(self._matrix)
        last_row = last_row_of_matrix(self._matrix)
        for (column_index, column_trans) in enumerate(last_column):
            for (row_index, row_trans) in enumerate(last_row):
                if column_trans is not None and row_trans is not None:
                    host_cell = self._matrix[column_index][row_index]
                    trans_ = transform_trans_while_excluding_vertex(
                        column_trans, row_trans, host_cell)
                    self._matrix[column_index][row_index] = trans_
        # Delete last row from transition matrix.
        self._matrix.pop()
        # Delete last column from transition matrix.
        for row in self._matrix:
            row.pop()

    def _index_of_first_loop(self):
        """Returns index of first loop in transition matrix."""
        for (row_index, row_of_transitions) in enumerate(self._matrix):
            if row_of_transitions[row_index] is not None:
                return row_index


def transform_trans_while_excluding_loop(transition, loop):
    """Преобразует передачу ``transition`` при исключении петли."""
    probability = transition.probability / (1 - loop.probability)
    resource = transition.resource + (
        (loop.resource * loop.probability) / (1 - loop.probability)
    )
    return Transition(probability=probability, resource=resource)


def transform_trans_while_excluding_vertex(column_trans, row_trans,
                                           host_cell=None):
    """Преобразует передачу ``host_cell`` при исключении вершины."""
    if host_cell is None:
        host_cell_probability = 0
        host_cell_resource = 0
    else:
        host_cell_probability = host_cell.probability
        host_cell_resource = host_cell.resource
    probability = (column_trans.probability * row_trans.probability
                   + host_cell_probability)
    resource = (
        (
            host_cell_probability * host_cell_resource
            + column_trans.probability * row_trans.probability
            * (column_trans.resource + row_trans.resource)
        ) / probability
    )
    return Transition(probability=probability, resource=resource)


def check_sum_of_probabilities(row):
    sum_prob = sum(transition.probability for transition in row if transition)
    return sum_prob == 0 or sum_prob == 1
