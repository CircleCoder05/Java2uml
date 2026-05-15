"""``python -m java2uml`` entry point."""

from .cli import main

if __name__ == "__main__":
    import sys

    sys.exit(main())
