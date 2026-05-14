import argparse
import os
import sys

from .utils.output import render


def detect_service() -> str:
    prog = os.path.basename(sys.argv[0])
    if prog.startswith("docker"):
        return "docker"
    if prog.startswith("kube"):
        return "kubectl"
    return "git"


def build_git_parser(subparsers):
    from .services.git.service import GitService
    from .services.git import commands  # triggers all @command decorators
    from .core.registry import get_commands

    service = GitService()

    if not service.is_repo():
        print(render({"command": None, "status": "error", "message": "not inside a git repository"}), end="")
        sys.exit(1)

    # Each command class registers its own subparser and flags
    commands = get_commands()
    for cmd_class in commands.values():
        cmd_class.register(subparsers)

    return service, commands


STUBS = {"docker", "kubectl"}

SERVICE_BUILDERS = {
    "git": build_git_parser,
    # "docker": build_docker_parser,
    # "kubectl": build_kubectl_parser,
}


def main():
    # Determine which service to load based on the binary name (gitwrap/dockerwrap/kubewrap)
    service_name = detect_service()

    # Services not yet implemented return a coming_soon stub and exit cleanly
    if service_name in STUBS:
        print(render({"service": service_name, "status": "coming_soon", "message": f"hey, this is the {service_name} wrapper — not implemented yet"}), end="")
        sys.exit(0)

    prog = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        prog=prog,
        description=f"A safer {service_name} CLI wrapper with YAML output",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Build the subcommand parsers and get back the service instance + command map
    service, commands = SERVICE_BUILDERS[service_name](subparsers)

    args = parser.parse_args()

    # Instantiate the right command class and run it
    command = commands[args.command](service)
    result = command.execute(args)
    print(render(result), end="")

    # Non-zero exit for error and aborted so callers can detect failure
    if result.get("status") in ("error", "aborted"):
        sys.exit(1)


if __name__ == "__main__":
    main()
