from pathlib import Path
import sys

def resource_path(
relative_path
):
"""
Return the absolute path to a bundled game resource.

```
During development:
    project/
        game/
            resources.py
        assets/

When packaged with PyInstaller:
    dist/
        Roundclacks/
            Roundclacks.exe
            assets/
"""

if getattr(
    sys,
    "frozen",
    False
):
    base_path = Path(
        sys.executable
    ).resolve().parent

else:
    base_path = Path(
        __file__
    ).resolve().parent.parent

return (
    base_path
    / relative_path
)
```
