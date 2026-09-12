# TTT Exploratory Discovery Packaging

This package creates ordered ZIPs for review of the earlier TTT / tango.dj-at work.

Subjects:

01  SOURCE_ARCHAEOLOGY
02  GRAMMAR_ARCHAEOLOGY
03  TRANSFORMATION_ARCHAEOLOGY
04  SEMANTIC_ARCHAEOLOGY
05  EVIDENCE_AND_PROVENANCE_ARCHAEOLOGY

The material is treated as exploratory discovery/reference material. It is not presumed to be current merely because it is packaged.

The intended eventual disposition of recovered material is:

- REUSE — directly useful to the current architecture
- INCORPORATE — discovery/design belongs in current documents/code
- REFERENCE — retain as historical evidence/test material
- SUPERSEDE — explicitly replaced by the generalized architecture

Nothing is deleted by these scripts.

The consolidated `_to_chat\02_ALL_TTT_MATERIAL.zip` is used as a historical source when present, so individual old files need not remain loose in `_to_chat`.

## Usage

From the MusicStewardship project:

    .\08_tools\setup\Package-TTT-Discovery.cmd 01 A
    .\08_tools\setup\Package-TTT-Discovery.cmd 02 A
    .\08_tools\setup\Package-TTT-Discovery.cmd 03 A
    .\08_tools\setup\Package-TTT-Discovery.cmd 04 A
    .\08_tools\setup\Package-TTT-Discovery.cmd 05 A

Or create all five:

    .\08_tools\setup\Package-TTT-Discovery.cmd ALL A

For a later transfer revision, use B, C, etc.

The ZIPs are written to `_to_chat`, which is intentionally ignored by Git.
