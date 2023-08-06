# -*- coding: utf-8 -*-


def matrix_is_quadratic(matrix):
    """Returns True if matrix is quadratic."""
    try:
        len_matrix = len(matrix)
        quadratic = all(len_matrix == len(row) for row in matrix)
    except TypeError:
        quadratic = False
    finally:
        return quadratic


def last_column_of_matrix(matrix):
    """Returns last column of quadratic matrix."""
    index_of_last_column = len(matrix) - 1
    return [row[index_of_last_column] for row in matrix]


def last_row_of_matrix(matrix):
    """Returns last row of quadratic matrix."""
    index_of_last_row = len(matrix) - 1
    return matrix[index_of_last_row]
