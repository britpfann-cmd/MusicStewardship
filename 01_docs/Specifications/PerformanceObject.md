# Performance Object Specification

## Purpose

Performance Objects are canonical entities that represent functional,
organizational, or informational elements of a musical performance.

Unlike musical recordings, Performance Objects exist to support the
presentation, navigation, organization, and documentation of a live
performance.

When exported to playback applications, they appear as ordinary playable
tracks compatible with the capabilities of the destination application.

Their purpose is to provide visual structure, semantic meaning, and
workflow support while allowing uninterrupted playlist execution.

Performance Objects are first-class canonical entities within the Music
Stewardship architecture.

## Rationale

Why does this exist?

Every major section should have a short rationale explaining the design choice. Years from now, when you're wondering why Performance Objects are modeled this way instead of some other way, those explanations will save you from repeating old debates or accidentally undoing an intentional design.

## Requirements

A Performance Object shall:

• possess canonical metadata.

• be uniquely identifiable.

• contain valid playable audio.

• be accepted by ordinary music library software.

• participate in playlists.

• export to multiple applications.

• support application-specific metadata mapping.

• support future extension without redesign.

• remain distinguishable from musical recordings.

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