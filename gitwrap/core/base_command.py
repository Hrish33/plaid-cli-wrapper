from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base for all service commands.

    Each concrete command implements run() with its own logic. The
    execute() entrypoint is what __main__ calls — it exists so subclasses
    can override it to add cross-cutting behaviour (e.g. logging) without
    touching run().
    """

    def __init__(self, service):
        """Args:
            service: A service instance (e.g. GitService) used to run subcommands.
        """
        self.service = service

    @abstractmethod
    def run(self, args) -> dict:
        """Execute the command and return a result dict.

        Args:
            args: Parsed argparse namespace for this command.

        Returns:
            Dict with at minimum 'command' and 'status' keys.
            Status is one of: ok, dry_run, error, aborted.
        """
        pass

    def execute(self, args) -> dict:
        """Entrypoint called by __main__. Delegates to run()."""
        return self.run(args)
