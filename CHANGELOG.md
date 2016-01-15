# Change Log
All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]
### Added
- Recipe for the rice genome (*Oryza sativa* L. ssp. *japonica*).
- Recipe for a model legume genome (*Medicago truncatula*).
- Batch for all Hymenoptera.
- Multiprocessing support for build script.

### Changed
- Complete overhaul of the genome configuration handling (now in the `registry` module).
- Minor changes to the Travis CI configuration.
- Excluded *Danio rerio* config from CI tests, as its resource requirements are right at the limit of what the Travis VMs can handle.
- Updated *Xenopus tropicalis* config to drop the parentheses in the species name.
- Updated *Drosophila melanogaster* config to the latest RefSeq assembly/annotation.

## [0.1.2] - 2016-01-09
### Added
- Package metadata.

### Fixed
- Minor improvements to documentation.

## [0.1.1] - 2016-01-08
### Fixed
- Added pre-requisites to setup.py.

## [0.1.0] - 2016-01-08

### Added
- first stable release!
- `GenomeDB` class and various extensions for downloading and formatting data.
- Modules for parsing and describing iLoci, proteins, mRNAs, exons, introns, and coding sequences.
- The script implementing the `stats` task, brought over with minimal changes from HymHub.
- Unit tests, with 100% success rate and 100% coverage of core package code (not scripts yet).
- Minimal installation and usage documentation.