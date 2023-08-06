# -*- coding: utf-8 -*-


class BeizerException(Exception):
    """Base exception class of beizer module."""


class MatrixInitError(BeizerException):
    """Errors of matrix initialization."""


class MatrixReduceError(BeizerException):
    """Matrix size reducing errors."""


class LoopExcludeError(MatrixReduceError):
    """Errors excluding a loop."""
