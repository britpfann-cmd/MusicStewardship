# Crackling Tunes Structural Pattern Analysis

This report identifies recurring structural patterns in the curated Crackling Tunes metadata. It does not establish transformation rules.

The purpose is to discover recurring source conventions that may later inform ingest mapping and transposition rules.

## Dataset

- Source/file records: **548**

## ARTIST Component Counts

| Components | Recordings |
|---:|---:|
| 1 | 15 |
| 2 | 512 |
| 3 | 21 |

## Vocal-Component Patterns

The first ARTIST component is provisionally treated as the ensemble portion. Components following it are classified for analytical purposes only.

| Pattern after ensemble | Recordings |
|---|---:|
| `PERSON_OR_OTHER` | 271 |
| `INSTRUMENTAL` | 241 |
| `PERSON_OR_OTHER / PERSON_OR_OTHER` | 21 |
| `(none)` | 15 |

## Most Common Ensemble Portions of ARTIST

| Frequency | Ensemble portion |
|---:|---|
| 64 | `Francisco Canaro` |
| 61 | `Juan D'Arienzo` |
| 28 | `Carlos Di Sarli` |
| 26 | `Osvaldo Pugliese` |
| 21 | `Alfredo De Angelis` |
| 20 | `Julio De Caro` |
| 18 | `Rodolfo Biagi` |
| 17 | `Francisco Lomuto` |
| 16 | `Orquesta Típica Victor` |
| 16 | `Osvaldo Fresedo` |
| 16 | `Aníbal Troilo` |
| 14 | `Roberto Firpo` |
| 12 | `Edgardo Donato` |
| 10 | `Rafael Canaro` |
| 10 | `Miguel Caló` |
| 10 | `Ricardo Tanturi` |
| 8 | `Quintin Verdu` |
| 7 | `Anibal Troilo` |
| 6 | `Juan Bautista Guido` |
| 6 | `Mario Melfi` |
| 6 | `Eva Bohr` |
| 6 | `Domingo Federico` |
| 6 | `Bachicha` |
| 6 | `Florindo Sassone` |
| 5 | `Pedro Maffia` |
| 5 | `Ángel D'Agostino` |
| 4 | `Quinteto Pirincho` |
| 4 | `Donato Racciatti` |
| 4 | `Manuel Pizarro` |
| 4 | `Marcel Feijoo` |
| 4 | `Pirincho` |
| 4 | `Pablo Brodman` |
| 3 | `Canaro, Francisco` |
| 3 | `Pedro Laurenz` |
| 2 | `D'Arienzo, Juan [Orquesta]` |
| 2 | `Di Sarli, Carlos` |
| 2 | `Agesilao Ferrazzano` |
| 2 | `Enrique Rodríguez` |
| 2 | `Juan De Dios Filiberto` |
| 2 | `Tity Quentin` |

## Most Common Singer / Non-Ensemble Components

| Frequency | Component |
|---:|---|
| 16 | `Charlo` |
| 16 | `Carlos Dante` |
| 12 | `Alberto Echagüe` |
| 12 | `Roberto Maida` |
| 12 | `Francisco Fiorentino` |
| 11 | `Alberto Morán` |
| 9 | `Alberto Castillo` |
| 7 | `Jorge Omar` |
| 7 | `Ángel Vargas` |
| 6 | `Roberto Chanel` |
| 6 | `Armando Laborde` |
| 5 | `Oscar Larroca` |
| 5 | `Jorge Durán` |
| 5 | `Roberto Rufino` |
| 5 | `Ernesto Famá` |
| 5 | `Carlos Roldán` |
| 4 | `Héctor Mauré` |
| 4 | `Henri Decker` |
| 4 | `Floreal Ruiz` |
| 4 | `Ricardo Ruiz` |
| 4 | `Raúl Berón` |
| 4 | `Roberto Ray` |
| 4 | `Agustín Irusta` |
| 3 | `Teófilo Ibáñez` |
| 3 | `Carlos Almada` |
| 3 | `Nina Miranda` |
| 3 | `Enzo Valentino` |
| 3 | `Mario Bustos` |
| 3 | `Jorge Ortiz` |
| 3 | `Horacio Lagos` |
| 3 | `Alberto Marino` |
| 3 | `Jorge Casal` |
| 3 | `Alberto Podestá` |
| 2 | `Aldo Campoamor` |
| 2 | `Armando Moreno` |
| 2 | `Roberto Diaz` |
| 2 | `Ángel Ramos` |
| 2 | `Alberto Rivera` |
| 2 | `Alberto Arenas` |
| 2 | `Carlos Acuña` |

## ARTIST Ensemble vs ALBUMARTIST

These are the most frequent pairings between the provisional ensemble portion of ARTIST and the stored ALBUMARTIST value.

| Frequency | ARTIST ensemble portion | ALBUMARTIST |
|---:|---|---|
| 62 | `Francisco Canaro` | `Canaro, Francisco [Orquesta]` |
| 55 | `Juan D'Arienzo` | `D'Arienzo, Juan [Orquesta]` |
| 28 | `Carlos Di Sarli` | `Di Sarli, Carlos [Orquesta]` |
| 24 | `Osvaldo Pugliese` | `Pugliese, Osvaldo [Orquesta]` |
| 19 | `Alfredo De Angelis` | `De Angelis, Alfredo [Orquesta]` |
| 18 | `Julio De Caro` | `De Caro, Julio [Orquesta]` |
| 18 | `Rodolfo Biagi` | `Biagi, Rodolfo [Orquesta]` |
| 15 | `Osvaldo Fresedo` | `Fresedo, Osvaldo [Orquesta]` |
| 14 | `Aníbal Troilo` | `Troilo, Aníbal [Orquesta]` |
| 12 | `Francisco Lomuto` | `Lomuto, Francisco [Orquesta]` |
| 10 | `Rafael Canaro` | `Canaro, Rafael [Orquesta]` |
| 10 | `Orquesta Típica Victor` | `Típica Victor [Orquesta]` |
| 9 | `Edgardo Donato` | `Donato, Edgardo [Orquesta]` |
| 8 | `Ricardo Tanturi` | `Tanturi, Ricardo [Orquesta]` |
| 8 | `Miguel Caló` | `Caló, Miguel [Orquesta]` |
| 7 | `Anibal Troilo` | `Troilo, Anibal 'Pichuco' [Orquesta]` |
| 7 | `Roberto Firpo` | `Firpo, Roberto [Cuarteto]` |
| 6 | `Eva Bohr` | `Bohr, Eva [Orquesta]` |
| 6 | `Domingo Federico` | `Federico, Domingo [Orquesta]` |
| 6 | `Quintin Verdu` | `Verdu, Quintin [Orquesta]` |
| 6 | `Florindo Sassone` | `Sassone, Florindo [Orquesta]` |
| 5 | `Pedro Maffia` | `Maffia, Pedro [Orquesta]` |
| 5 | `Ángel D'Agostino` | `D'Agostino, Ángel [Orquesta]` |
| 4 | `Francisco Lomuto` | `Lomuto, Francisco [Orquesta}` |
| 4 | `Quinteto Pirincho` | `Pirincho [Quinteto]` |
| 4 | `Roberto Firpo` | `Firpo, Roberto [Orquesta]` |
| 4 | `Donato Racciatti` | `Racciatti, Donato [Orquesta]` |
| 4 | `Manuel Pizarro` | `Pizarro, Manuel [Orquesta]` |
| 4 | `Marcel Feijoo` | `Feijoo, Marcel [Orquesta]` |
| 4 | `Pablo Brodman` | `Brodman-Alfaro [Orquesta]` |
| 3 | `Canaro, Francisco` | `Canaro, Francisco [Orquesta]` |
| 3 | `Bachicha` | `Bachicha [Orquesta]` |
| 3 | `Pedro Laurenz` | `Laurenz, Pedro [Orquesta]` |
| 2 | `Quintin Verdu` | `Verdu, Quintin [Orchestre]` |
| 2 | `Juan De Dios Filiberto` | `Filiberto, Juan De Dios [Orquesta}` |
| 2 | `Tity Quentin` | `Quentin, Tity [Orquesta]` |
| 2 | `Lucchesi, Jose [Orquesta]` | `Lucchesi, Jose [Orquesta]` |
| 2 | `Aníbal Troilo` | `Troilo, Anibal 'Pichuco' [Orquesta]` |
| 2 | `Gorni Kramer e i suoi solisti` | `Kramer, Gorni [Orquesta]` |
| 2 | `Carlos Flores` | `Flores, Carlos [Orquesta]` |
| 2 | `Di Sarli` | `Di Sarli, Carlos [Orquesta]` |
| 2 | `Francisco Lauro` | `Lauro, Francisco [Sexteto]` |
| 2 | `Orquesta Típica Victor` | `Tipica Victor [Orquesta]` |
| 2 | `D'Arienzo, Juan` | `D'Arienzo, Juan [Orquesta]` |
| 2 | `Pugliese, Osvaldo` | `Pugliese, Osvaldo [Orquesta]` |
| 2 | `Típica Brunswick` | `Típica Brunswick [Orquesta]` |
| 2 | `Adolfo Carabelli` | `Carabelli, Adolfo [Orquesta]` |
| 2 | `Pirincho` | `Pirincho [Quinteto Típica]` |
| 2 | `Orquesta Típica Victor` | `Tîpica Victor [Orquesta]` |
| 2 | `Alfredo Attadia` | `Attadia, Alfredo [Orquesta]` |
| 2 | `Eduardo Bianco` | `Bianco, Eduardo [Orquesta]` |
| 2 | `Juan Bautista Guido` | `Guido, Juan Bautista [Orquesta]` |
| 2 | `Edelmiro D'Amario` | `Vargas, Ángel [Orquesta]` |
| 2 | `Enrique Alessio` | `Castillo, Alberto [Orquesta]` |
| 2 | `Firpo` | `Firpo, Roberto [Cuarteto]` |
| 2 | `Juan 'Bautista' Guido` | `Guido, Juan 'Bautista' [Orquesta]` |
| 2 | `José Sala` | `Sala, José [Orquesta]` |
| 2 | `Héctor Varela` | `Varela, Héctor [Orquesta]` |
| 2 | `Emilio Balcarce` | `Castillo, Alberto [Orquesta]` |
| 2 | `Enrique Madriguera` | `Madriguera, Enrique [Orquesta]` |

## Observations Requiring Further Investigation

- Determine whether `/` consistently separates ensemble from vocal participant(s).
- Determine whether `Instrumental` and `Instr.` are equivalent source conventions.
- Determine whether multiple post-ensemble components represent multiple singers or other roles.
- Determine how reliably the first ARTIST component corresponds to the ensemble represented by ALBUMARTIST.
- Compare ARTIST structure with filename structure as an independent source of evidence.
- Preserve exceptions rather than forcing them into a dominant pattern.

## Interpretation Principle

A recurring source pattern should be treated as a candidate interpretation until it has been evaluated across multiple releases and known exceptions.

Pattern discovery precedes transformation-rule definition.
