_REGISTRY = {}


def command(name):
    """Decorator that registers a command class under the given name."""
    def decorator(cls):
        if name in _REGISTRY:
            raise ValueError(f"duplicate command name '{name}': already registered by {_REGISTRY[name].__name__}")
        _REGISTRY[name] = cls
        return cls
    return decorator


def get_commands():
    return dict(_REGISTRY)
