# Profile source and artwork

The overview is an original technical folio for Naren K S. It uses oversized Space Grotesk type, IBM Plex Mono labels, a graphite surface and a restrained cobalt palette. The opening wire sculpture and all four project illustrations are generated vector artwork, not screenshots or representations of measured data.

## Edit and rebuild

`profile.json` owns the profile copy, project order, repository links, tools and contacts. `scripts/build.py` generates `README.md` and the twenty SVG panels in `assets/`.

```sh
python -m pip install -r scripts/requirements.txt
python scripts/build.py
```

The two open-source typefaces from the Google Fonts repository are bundled in `scripts/fonts/` alongside their licenses. After installing the Python dependency, generation runs entirely offline. The generated assets contain outlined type, so visitors need no fonts, scripts, API keys or external widgets.

Every panel has a separate mobile composition selected through `<picture>`. Each image has a title, description and meaningful README alternative text. The native introduction, contact links and expandable text index remain usable independently of the illustrations.

The hero and project illustrations use CSS keyframes inside their SVG files. The ribbon sways, audio meters follow a moving playhead, signals travel through the portal diagram, a scan passes over the map, and the terminal rows brighten in sequence. These loops run when the browser reports no reduced-motion preference. The panels render in their static form when reduced motion is enabled.

## Publication

GitHub displays this repository's `README.md` on the `naren214` profile. Rebuild after source changes, inspect desktop and mobile rendering, then commit the source and generated files together. There is no scheduled rebuild: this profile contains curated work and current interests rather than activity counters.

## Content boundaries

- UNHEARD is a browser instrument studio with gesture mapping and local composition storage.
- The recruitment portal extends an existing codebase. Its server validation and Firestore transaction behavior are described without claiming sole original authorship or production deployment.
- Drone Mapper is a hackathon prototype. Missing GPS metadata uses demo coordinates; model estimates are not validated emergency-response decisions.
- TermVision is a terminal video player, including optional Windows audio.
- HaluEval work is presented as exploration. No unverified accuracy or completed demo is claimed.

## Typography sources

- [Space Grotesk](https://github.com/google/fonts/tree/main/ofl/spacegrotesk)
- [IBM Plex Mono](https://github.com/google/fonts/tree/main/ofl/ibmplexmono)

Both typefaces are distributed under the SIL Open Font License; their license texts are retained alongside the generator. No artwork or code from the reference profile is used.
