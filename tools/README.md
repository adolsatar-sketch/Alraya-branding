# Build

`index.html` is generated. Edit the sources here, then run:

    pip install uharfbuzz shapely fonttools brotli
    python3 tools/build.py

- `marks.py`: the five logo directions as geometry. Text is shaped with HarfBuzz and turned into outlines.
- `apps.py`: the application scenes. They all use the approved logo symbols.
- `site.css`, `site.js`: page styles and behaviour.
- `fonts/`: OFL fonts (licences included).

The earlier version is kept unchanged in `v1/index.html`.
