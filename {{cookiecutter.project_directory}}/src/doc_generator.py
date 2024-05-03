try:
    import json
    import argparse
    import sys
    import typing
    from pathlib import Path

    from src.main import create_app, __TITLE__
except ImportError:
    from pathlib import Path

    FILE = Path(__file__).resolve()
    ROOT = FILE.parents[1]  # app folder
    if str(ROOT) not in sys.path:
        sys.path.append(str(ROOT))  # add ROOT to PATH

    from src.main import create_app, __TITLE__

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8">
    <title>%s</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="shortcut icon" href="https://fastapi.tiangolo.com/img/favicon.png">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
    </style>
    <style data-styled="" data-styled-version="4.4.1"></style>
</head>
<body>
    <div id="redoc-container"></div>
    <script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
    <script>
        var spec = %s;
        Redoc.init(spec, '{}', document.getElementById("redoc-container"));
    </script>
</body>
</html>
"""


def create_openapi_json(
    schema: typing.Dict[str, typing.Any], *, save_path: Path
) -> None:
    with open(str(save_path), "w") as f:
        json.dump(schema, f)

    if not save_path.is_file():
        raise FileNotFoundError(f"Save file failed: {save_path}")


def create_openapi_html(
    schema: typing.Dict[str, typing.Any], version: str, *, save_to: Path
) -> None:
    _version = version.replace(".", "")
    doc_version_name = f"v{_version}" if version[0].lower() != "v" else _version
    doc_project_name = __TITLE__.replace(" ", "-").lower()

    current_version = f"{doc_project_name}_{doc_version_name}.html"
    latest_version = f"{doc_project_name}_latest.html"

    for file_name in [current_version, latest_version]:
        with open(str(save_to / file_name), "w") as f:
            print(HTML_TEMPLATE % (__TITLE__, json.dumps(schema)), file=f)

        assert (save_to / file_name).is_file(), f"Save file failed: {file_name}"


def main():
    parser = argparse.ArgumentParser(description="Documentation Generator")
    parser.add_argument(
        "--save-to", type=str, default="docs", help="Save documentation to where"
    )
    parser.add_argument(
        "--version", type=str, help="Version of the documentation", required=True
    )
    args = parser.parse_args()

    print(f"Generating documentation...Version: {args.version}")

    # Make sure the path is absolute
    save_folder = Path(args.save_to).resolve()
    if not save_folder.is_dir():
        save_folder.mkdir(parents=True, exist_ok=False)

    app = create_app(version=args.version)
    schema = app.openapi()

    create_openapi_html(schema=schema, version=args.version, save_to=save_folder)
    print(f"Save openapi html files successfully: {save_folder}")


if __name__ == "__main__":
    main()
