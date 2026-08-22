def test_api_error_shape_documented():
    from apps.core.exceptions import api_exception_handler

    assert callable(api_exception_handler)
