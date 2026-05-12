import argparse
import os
import sys

from .output import render


def detect_service() -> str:
    prog = os.path.basename(sys.argv[0])
    if prog.startswith("docker"):
        return "docker"
    if prog.startswith("kube"):
        return "kubectl"
    return "git"


def build_git_parser(subparsers):
    from .services.git.service import GitService
    from .services.git.commands.status import StatusCommand
    from .services.git.commands.clean import CleanCommand
    from .services.git.commands.reset import ResetCommand
    from .services.git.commands.push import PushCommand
    from .services.git.commands.commit import CommitCommand

    service = GitService()

    if not service.is_repo():
        print(render({"command": None, "status": "error", "message": "not inside a git repository"}), end="")
        sys.exit(1)

    subparsers.add_parser("status", help="Show working tree status as YAML")

    clean_parser = subparsers.add_parser("clean", help="Remove untracked files")
    clean_parser.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    clean_parser.add_argument("--force", action="store_true", help="Actually remove files")

    reset_parser = subparsers.add_parser("reset", help="Reset working tree to HEAD")
    reset_parser.add_argument("--dry-run", action="store_true", help="Show what would be reset")
    reset_parser.add_argument("--force", action="store_true", help="Actually reset to HEAD")

    push_parser = subparsers.add_parser("push", help="Push to remote")
    push_parser.add_argument("--dry-run", action="store_true", help="Simulate push without sending")
    push_parser.add_argument("--force", action="store_true", help="Force push")

    commit_parser = subparsers.add_parser("commit", help="Stage all changes and commit")
    commit_parser.add_argument("-m", dest="message", help="Commit message")
    commit_parser.add_argument("--dry-run", action="store_true", help="Show what would be committed")
    commit_parser.add_argument("--force", action="store_true", help="Actually stage and commit")

    return service, {
        "status": StatusCommand,
        "clean": CleanCommand,
        "reset": ResetCommand,
        "push": PushCommand,
        "commit": CommitCommand,
    }


STUBS = {"docker", "kubectl"}

SERVICE_BUILDERS = {
    "git": build_git_parser,
    # "docker": build_docker_parser,
    # "kubectl": build_kubectl_parser,
}


def main():
    service_name = detect_service()

    if service_name in STUBS:
        print(render({"service": service_name, "status": "coming_soon", "message": f"hey, this is the {service_name} wrapper — not implemented yet"}), end="")
        sys.exit(0)

    prog = os.path.basename(sys.argv[0])
    parser = argparse.ArgumentParser(
        prog=prog,
        description=f"A safer {service_name} CLI wrapper with YAML output",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    service, commands = SERVICE_BUILDERS[service_name](subparsers)

    args = parser.parse_args()

    command = commands[args.command](service)
    result = command.execute(args)
    print(render(result), end="")

    if result.get("status") in ("error", "aborted"):
        sys.exit(1)


if __name__ == "__main__":
    main()
