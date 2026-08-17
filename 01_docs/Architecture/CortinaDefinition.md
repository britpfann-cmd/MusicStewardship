# Cortina Definition Model

## Purpose

A Cortina Definition describes the information required to construct a cortina from managed resources. The definition serves as the authoritative specification for a cortina and remains independent of implementation technologies, export formats, and playback applications.

## Relationship to Performance Object

A Cortina Definition supports the realization of a Cortina Object by identifying the resources, constraints, and characteristics required for construction.

A Cortina Definition is not itself a Performance Object. Rather, it is a specification used to produce one or more realizations of a Cortina Object.

## Rationale

Separating cortina definitions from assembled cortinas promotes reuse, consistency, and maintainability. The same definition may be used to generate multiple cortina realizations, export formats, and application-specific representations while preserving a single authoritative description.

This approach allows source resources, construction processes, and export mechanisms to evolve independently.

## Requirements

A Cortina Definition shall:

- be uniquely identifiable.
- possess a defined purpose.
- remain independent of playback application implementation.
- identify the resources required for construction.
- describe the role of each required resource.
- support the construction of one or more cortina realizations.
- support multiple export targets.
- preserve semantic intent independent of implementation details.
- support future extension without redesign.

A Cortina Definition may require one or more of the following resource categories:

- Audio Resources
  - provide musical, spoken, or environmental audio content.

- Silence Resources
  - provide timed intervals without audio content.

- Visual Resources
  - provide images, symbols, logos, or other graphical content.

- Text Resources
  - provide audience-facing or DJ-facing textual content.

- Presentation Resources
  - provide styling information such as colors, fonts, templates, and display conventions.

- Future Resource Types
  - provide capabilities introduced by future implementations.

Not all cortina definitions require all resource categories.

## Representation
A Cortina Definition is represented as a declarative specification describing the desired characteristics and resource requirements of a cortina.

The definition does not prescribe how resources are selected, assembled, transformed, or exported. Such concerns are implementation responsibilities.

Implementations may use grammars, templates, rules, profiles, or other mechanisms to realize cortinas from definitions.

## Terminology

### Cortina Definition

The authoritative specification describing the resources, requirements, constraints, and intended characteristics necessary to construct a cortina.

### Resource

A managed asset available for use during cortina construction.

### Cortina Realization

A constructed cortina produced from a Cortina Definition and its associated resources.
