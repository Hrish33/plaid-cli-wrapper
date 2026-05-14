import yaml


def render(result: dict) -> str:
    """Serialize a result dict to a YAML string.

    All commands produce a dict and pass it here before printing.
    allow_unicode=True prevents em dashes and other unicode from being
    escaped as \\uXXXX sequences in the output.
    """
    return yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)

