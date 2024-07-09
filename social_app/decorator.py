'''
This model defines a decorator that is applied on all class method
'''
from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404


def handle_exceptions(view_func: callable) -> callable:
    """
    Handles exceptions that may occur in the decorated
    view function.

    Args:
        view_func: The view function to be wrapped.

    Returns:
        Response: Returns a response with an error message
          and appropriate status code in case of exceptions.

    Raises:
        None
    """

    @wraps(view_func)
    def _wrapped_view(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except Http404 as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return Response(
                {'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)
    return _wrapped_view


def class_exception_handler(cls):
    """
    A decorator that wraps all methods of a class with an
    exception handling mechanism.

    Args:
        cls: The class to decorate.

    Returns:
        The decorated class with exception handling for all its methods.
    """

    for name, values in vars(cls).items():
        if callable(values):
            setattr(cls, name, handle_exceptions(values))

    return cls
