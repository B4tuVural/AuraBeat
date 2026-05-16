#!/usr/bin/env python
"""AuraBeat - Django yönetim komutları giriş noktası."""
import os
import sys


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aurabeat.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Django import edilemedi. Sanal ortamı aktive ettiğinizden "
            "ve `pip install -r requirements.txt` çalıştırdığınızdan emin olun."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
