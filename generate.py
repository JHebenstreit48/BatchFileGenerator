import os
import shutil
from typing import List, Tuple
from templates import get_template


def prompt_user() -> Tuple[str, str, List[Tuple[str, List[str]]], str, dict]:
    mode = input(
        "📍 Generate directly to project or stage to output? "
        "(project/staging): "
    ).strip().lower()

    base_path = (
        input("📁 Project base path: ").strip()
        if mode == "project" else "output"
    )

    pairs_input = input(
        "📂 Enter folder:filenames (e.g., A:x,y | B:z): "
    ).split("|")

    folder_map = []
    for pair in pairs_input:
        if ":" not in pair:
            continue
        folder, files = pair.split(":")
        filenames = [f.strip() for f in files.split(",") if f.strip()]
        folder_map.append((folder.strip(), filenames))

    extension = input(
        "📝 File extension (e.g., tsx, js, py): "
    ).strip().lstrip(".")

    overrides = {}
    if extension == "tsx":
        override_names = input(
            "🔁 Exported component names (comma-separated): "
        ).strip()
        header_texts = input(
            "📝 Header texts (comma-separated): "
        ).strip()
        markdown_paths = input(
            "📄 Markdown paths (comma-separated, blank = auto): "
        ).strip()

        overrides = {
            "export_names": [
                n.strip() for n in override_names.split(",") if n.strip()
            ],
            "header_texts": [
                h.strip() for h in header_texts.split(",") if h.strip()
            ],
            "markdown_paths": [
                m.strip() for m in markdown_paths.split(",") if m.strip()
            ],
        }

    return mode, base_path, folder_map, extension, overrides


def generate_files(
    mode: str,
    base_path: str,
    folder_map: List[Tuple[str, List[str]]],
    extension: str,
    overrides: dict
):
    os.makedirs(base_path, exist_ok=True)

    export_names = overrides.get("export_names", [])
    header_texts = overrides.get("header_texts", [])
    markdown_paths = overrides.get("markdown_paths", [])

    file_index = 0

    for folder, files in folder_map:
        folder_path = os.path.join(base_path, folder)
        os.makedirs(folder_path, exist_ok=True)

        for name in files:
            file_path = os.path.join(folder_path, f"{name}.{extension}")

            if os.path.exists(file_path):
                response = input(
                    f"⚠️ {file_path} exists. Overwrite with template? "
                    f"(y/n): "
                ).lower()
                if response != "y":
                    print(f"⏭️ Skipped: {file_path}")
                    file_index += 1
                    continue

            export_name = (
                export_names[file_index]
                if file_index < len(export_names)
                else name
            )
            header_text = (
                header_texts[file_index]
                if file_index < len(header_texts)
                else name
            )
            markdown_path = (
                markdown_paths[file_index]
                if file_index < len(markdown_paths)
                else None
            )

            content = get_template(
                extension,
                export_name,
                folder,
                header_text,
                markdown_path
            )

            if not content:
                if extension == "tsx":
                    content = (
                        f"export default function {export_name}() {{\n"
                        f"  return (\n"
                        f"    <div>\n"
                        f"      <h1>{header_text}</h1>\n"
                        f"    </div>\n"
                        f"  );\n"
                        f"}}\n"
                    )
                elif extension in ["js", "ts"]:
                    content = (
                        f"export const {export_name} = () => {{\n"
                        f"  console.log('{header_text} loaded');\n"
                        f"}};\n"
                    )
                elif extension == "py":
                    content = (
                        f"def {export_name.lower()}():\n"
                        f"    print('{header_text} function')\n"
                    )
                else:
                    content = (
                        f"// {name}.{extension} - customize as needed\n"
                    )

            with open(file_path, "w") as f:
                comment = (
                    f"// Auto-generated {extension.upper()} file: "
                    f"{name}\n\n"
                )
                f.write(comment + content)

            print(f"✅ Created: {file_path}")
            file_index += 1

    if mode == "staging":
        move = input(
            "🚚 Move folders to another project? (y/n): "
        ).lower()
        if move == "y":
            dest = input("📍 Destination path: ").strip()
            for folder, _ in folder_map:
                src = os.path.join(base_path, folder)
                dest_path = os.path.join(dest, folder)
                try:
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copytree(
                        src,
                        dest_path,
                        dirs_exist_ok=True
                    )
                    print(f"📁 Moved '{folder}' to '{dest_path}'")
                except Exception as e:
                    print(f"❌ Failed to move '{folder}': {e}")


if __name__ == "__main__":
    mode, base_path, folder_map, extension, overrides = prompt_user()
    generate_files(mode, base_path, folder_map, extension, overrides)
