# Third-Party Notices

AKM-DOS is licensed under the GNU General Public License v3.0 or later
(`GPL-3.0-or-later`). See `LICENSE` for the license terms that apply to
AKM-DOS itself.

This document records known third-party dependencies and assets. It is an
inventory, not a replacement for the original license texts shipped by those
projects.

## Python dependencies

### PyQt5

- Project: PyQt5 by Riverbank Computing
- Use in AKM-DOS: legacy AKM Browser GUI
- License used by the open-source edition: GNU GPL v3
- Status: compatible with AKM-DOS's GPL distribution model
- Note: PyQt also uses Qt. Binary distributions must preserve and satisfy the
  applicable Qt and other bundled third-party license obligations.

### PyQtWebEngine

- Project: PyQt-WebEngine by Riverbank Computing
- Use in AKM-DOS: legacy AKM Browser web engine
- License used by the open-source edition: GNU GPL v3
- Status: compatible with AKM-DOS's GPL distribution model
- Note: Qt WebEngine includes additional third-party components. Binary
  distributions may require additional notices and license material.

### PyAutoGUI

- Project: PyAutoGUI by Al Sweigart
- Declared in: `requirements.txt`
- License: BSD 3-Clause
- Status: permissive license; retain its copyright notice, license conditions
  and disclaimer when redistribution requires them.
- Current repository note: it is declared as a dependency, but its necessity
  should be reviewed before a release.

### PySide6 / Qt for Python

- Use: 0.8 GUI, SVG rendering and startup audio via Qt Multimedia.
- Declared in: `requirements-gui.txt`; development verified with PySide6 6.11.2.
- Open-source Qt for Python is offered under LGPLv3/GPLv3, with a commercial
  alternative. Shiboken and bundled Qt components have their own applicable
  terms; retain the license texts shipped in the installed distribution.
- Official license inventory: https://doc.qt.io/qtforpython-6/licenses.html
- Binary packaging must retain applicable Qt, Shiboken, multimedia and other
  bundled notices. No binary release is produced by this development change.

`playsound` is no longer required or used by the 0.8 boot entry point.

## Python standard library / Tkinter

AKM-DOS also uses Python standard-library modules and Tkinter. These are not
vendored into this repository. Packaging Python or Tcl/Tk with a binary release
may create additional notice requirements, which should be reviewed as part of
release packaging.

## Assets requiring provenance review

### `win95.mp3`

- Status: **UNVERIFIED — DO NOT TREAT AS GPL-LICENSED**
- The repository currently contains this audio file, but its author, source and
  redistribution license are not documented.
- The AKM-DOS GPL license does not automatically grant rights to this asset.
- Before a public packaged release, either document a valid redistribution
  license for the file or replace/remove it.
- 0.8 boot uses `assets/audio/akm_horizon.wav` instead. The original, synthesized
  cue and its generator are project contributions under GPL-3.0-or-later.
  Source/provenance details: `assets/audio/README.md`.
- The old unused file is retained for archival review, not used at runtime.

### Horizon Glass SVGs

- Source: the user-supplied AKM-DOS UI Figma frame `6:2`.
- Used under the user's authorization to implement that design locally.
- No third-party redistribution license is inferred from that authorization.
- Source node inventory and rights note: `assets/horizon/README.md`.
- Retained from the previous GUI; no longer used by the redesigned screens.

### AKM DOS 0.8 redesign SVGs

- Source: user-supplied Figma file `dwDgZF6gxfy0oeygvC4xlm`, Login frame `2:10`.
- Seven original silhouette SVGs used under local implementation authorization.
- Source node inventory and rights note: `assets/redesign/README.md`.
- No independent third-party redistribution license is inferred.

## Legacy source requiring provenance review

The following older GUI/application files predate the current Core Foundation
architecture and should have their authorship/source history confirmed before a
formal release:

- `aka.py`
- `Programs/calculator.py`
- `Programs/clock.py`
- `Programs/notepad.py`
- `Programs/webbrowser.py`

These files are **not being declared third-party code by this notice**. Their
provenance is simply not documented well enough in the repository to make a
strong licensing claim without further review.

If any file was adapted from a tutorial, example project, Stack Overflow answer
or another repository, its original source and license should be identified and
the required attribution/license notice should be added.

## Release checklist

Before publishing a packaged AKM-DOS release:

1. Resolve or remove every item marked unverified.
2. Confirm provenance of the legacy source files listed above.
3. Re-check the exact dependency versions being distributed and their licenses.
4. Include required third-party copyright/license notices in the distribution.
5. Review licenses of transitive/bundled components introduced by GUI and
   packaging tools.
6. Re-run this audit whenever dependencies or packaged assets change.

Last reviewed: 2026-10-07.
