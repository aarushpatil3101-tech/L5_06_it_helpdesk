# Issues found in helpdesk_system.py

Baseline: Pylint 5.53/10, Bandit 4 issues (1 High), Flake8 15 issues. After: Pylint 10.00/10, Bandit 0, Flake8 0.

| Issue | Type | Line(s) | Description | Fix Approach |
|-------|------|---------|-------------|--------------|
| Command injection via `shell=True` (Bandit B602, High) | Security | 38 | `"ping -c 1 " + hostname` run through a shell: a hostname like `x; rm -rf ~` executes arbitrary commands (CWE-78) | Validate hostname with a regex, call `subprocess.call(["ping","-c","1",hostname])` with no shell |
| Hardcoded admin password (B105) | Security | 8, 54 | Secret committed to source and repeated in `main()` | Read from `HELPDESK_ADMIN_PASSWORD` env var; reject all closes if unset |
| Bare `except: pass` (B110, W0702, E722) | Bug / Security | 23-24 | Swallows every error, so `add_note(999, ...)` fails silently | Catch `KeyError` only, report the missing ticket, return False |
| Mutable default argument (W0102) | Bug | 10 | `audit_trail=[]` is shared across all calls | Default `None`, create a new list inside the function |
| No urgency validation (not flagged by tools) | Logic bug | 13, 48, 52 | `-7`, `99` accepted as priority; non-numeric input crashes with `ValueError` | `parse_urgency()` enforces integer 1-5; `main()` re-prompts on bad input |
| `close_ticket` fails silently / `KeyError` (not flagged) | Logic bug | 26-28 | Wrong password does nothing; unknown id raises `KeyError` | Return bool and print reason for both cases |
| `main()` runs on import (not flagged) | Design | 58 | Importing the module executes the demo | Add `if __name__ == "__main__":` guard |
| `== None` (C0121, E711) | Style / Bug | 33 | Identity should be tested with `is` | Use `is None` |
| Unfinished file handling (R1732, W1514) | Quality | 41-43 | `open()` without `with`, no encoding; leaks handle on error | `with open(..., encoding="utf-8")` and `json.dump` |
| `global` state and constant naming (W0603, C0103) | Design | 6-7, 11 | Mutable module globals | `TicketStore` dataclass instance |
| camelCase name (C0103) | Style | 30 | `unresolvedHighPriority` not snake_case | Renamed `unresolved_high_priority`, list comprehension |
| Missing docstrings (C0114, C0116) | Style | all | No module/function docs | Added docstrings |
| `%` formatting (C0209), unused `t2` (W0612, F841) | Style | 14, 47 | Old-style formatting, dead variable | f-strings; dropped unused variable |
| Whitespace/length (E302, E305, E501) | Style | many | Blank lines and lines over 79 chars | Reformatted to PEP 8 |

Note: `main()` demo data changed from joe urgency `-7` to `2`, since `-7` is now correctly rejected.
