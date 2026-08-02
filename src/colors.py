"""
colors.py — Thin, optional color layer for VitalScope output.

Uses `colorama` when it is available so ANSI colors work on Windows too.
If `colorama` is not installed, every helper degrades to plain text, so
the CLI keeps working exactly the same — just without color. This keeps
color an *optional* enhancement rather than a hard dependency.

Usage:
    from colors import c
    print(c.title("Header"))
    print(c.good("Normal weight"))
    print(c.error("! bad input"))
"""

try:
    import colorama
    from colorama import Fore, Style

    # autoreset=True means we don't have to append a reset code manually.
    colorama.init(autoreset=True)
    _ENABLED = True
except ImportError:  # colorama not installed -> plain text fallback
    _ENABLED = False


def _wrap(code, text):
    """Wrap text in an ANSI code + reset, or return it plain if disabled."""
    if not _ENABLED:
        return text
    return f"{code}{text}{Style.RESET_ALL}"


class _Colors:
    """Semantic color helpers — named by meaning, not by raw color."""

    def title(self, text):
        return _wrap(Fore.CYAN + Style.BRIGHT, text) if _ENABLED else text

    def label(self, text):
        return _wrap(Fore.WHITE + Style.BRIGHT, text) if _ENABLED else text

    def value(self, text):
        return _wrap(Fore.YELLOW + Style.BRIGHT, text) if _ENABLED else text

    def good(self, text):
        return _wrap(Fore.GREEN, text) if _ENABLED else text

    def warn(self, text):
        return _wrap(Fore.YELLOW, text) if _ENABLED else text

    def bad(self, text):
        return _wrap(Fore.RED, text) if _ENABLED else text

    def error(self, text):
        return _wrap(Fore.RED + Style.BRIGHT, text) if _ENABLED else text

    def dim(self, text):
        return _wrap(Style.DIM, text) if _ENABLED else text


# Single shared instance the rest of the app imports.
c = _Colors()

# Whether color is actually active (handy for tests / diagnostics).
enabled = _ENABLED
