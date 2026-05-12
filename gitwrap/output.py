import yaml


def render(result: dict) -> str:
    return yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)
