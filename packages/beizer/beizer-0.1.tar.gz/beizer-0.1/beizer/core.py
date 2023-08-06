# -*- coding: utf-8 -*-


def reduce_matrix_size(transition_matrix):
    """Reduces matrix size."""
    while not transition_matrix.has_only_source_and_drain():
        while transition_matrix.loop_exists():
            transition_matrix.exclude_first_loop()
        transition_matrix.exclude_last_vertex()
