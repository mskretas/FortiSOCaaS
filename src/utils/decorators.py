from functools import wraps


def validate_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        http_method_accepted_values = ["GET", "POST"]
        if kwargs["http_method"] not in http_method_accepted_values:
            raise ValueError(f"Value must be one of values {http_method_accepted_values}, got {kwargs['http_method']}")

        http_resource_accepted_values = ["/alert", "/service-request"]
        if kwargs["http_resource"] not in http_resource_accepted_values:
            raise ValueError(f"Value must be one of values {http_resource_accepted_values}, got {kwargs['http_resource']}")

        return func(*args, **kwargs)
    return wrapper
