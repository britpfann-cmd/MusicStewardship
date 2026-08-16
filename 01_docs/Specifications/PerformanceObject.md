# Performance Object Specification

## Purpose

Performance Objects provide visual structure, semantic meaning, and workflow support within the performance model.

Performance Objects are abstract model elements whose realization depends on the capabilities of the target playback environment. Initially, they are exported using a lowest-common-denominator approach, typically as ordinary non-danceable or "quiet" audio tracks compatible with existing DJ software. Future integrations may map Performance Objects to richer application-specific features while preserving the same underlying semantics.

## Implementation

Performance Objects are canonical model entities whose meaning is independent of any specific playback application. Different playback environments may implement them differently while preserving the same underlying semantics.

## Rationale

Why does this exist?

Every major section should have a short rationale explaining the design choice. Years from now, when you're wondering why Performance Objects are modeled this way instead of some other way, those explanations will save you from repeating old debates or accidentally undoing an intentional design.

## Requirements

A Performance Object shall:

• possess canonical metadata.
• be uniquely identifiable.
• possess a defined Performance Object type.
• preserve semantic meaning independent of playback application.
• support application-specific metadata mapping.
• support future extension without redesign.
• remain distinguishable from musical recordings.

## Default Playback Export Requirements

The default playback export shall:

• contain valid playable audio.
• be accepted by ordinary music library and playlist management software.
• support participation in playlists.
• support export to multiple applications.

## Terminology

Performance Object

A canonical object representing a non-musical component of a
performance.

Performance Recording

A musical recording intended for playback.

Punctuation Object

A Performance Object used to visually or semantically separate
performance sections.

Announcement Object

A Performance Object used to communicate information to performers
or audience.

Marker Object

A Performance Object indicating transitions or operational events.

Performance Collection

An ordered collection of Performance Objects and musical recordings.

## Canonical Representation

Performance Object

UUID

Name

Display Name

Category

Subtype

Metadata

Audio

Artwork

Export Rules

Knowledge Links

History

## Metadata 

Table fields and purposes

| Field       | Purpose                      |
| ----------- | ---------------------------- |
| UUID        | Permanent identity           |
| Title       | Display name                 |
| Subtitle    | Optional                     |
| Category    | Punctuation, Announcement... |
| Type        | Header, Trailer...           |
| Description | Human explanation            |
| Language    | Optional                     |
| Duration    | Audio duration               |
| Created     | Timestamp                    |
| Version     | Specification version        |

## Audio Representation 
This is where we define things like:

silence
click
tone
spoken announcement
applause
etc.

Importantly, audio becomes just one rendering of the object.

## Generated Artifacts 
Canonical Object

↓

FLAC

↓

MP3

↓

Artwork

↓

Metadata

↓

Manifest

↓

Export

## Export Mapping

This section is surprisingly important.

One canonical object becomes different things.

Example
Canonical

↓

TangoDJ

Genre = Cortina

Title = ----- Tango -----

↓

Mixxx

Crate Entry

↓

MediaMonkey

Playlist Marker

↓

foobar

Tagged Track

## TangoDJ Implementation


## Future Extensions
This is where we finally get to dream a little.

Examples:

colored separators
SVG artwork
application plug-ins
cue sheets
spoken announcements
lighting cues
OSC messages
MIDI events
room automation

Everything we've imagined has a place—but it doesn't clutter the core specification.