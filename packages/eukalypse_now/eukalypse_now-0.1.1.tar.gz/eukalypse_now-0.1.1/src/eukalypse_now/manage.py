#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eukalypse_now.settings")

    #standalone hack
    sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
