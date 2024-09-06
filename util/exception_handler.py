def exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"An error occurred in function '{func.__name__}': {e}")
            return None  # You can return a default value or re-raise the exception if needed
    return wrapper