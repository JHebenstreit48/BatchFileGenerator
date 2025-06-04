import os
import shutil
from typing import List, Tuple
from templates import get_template


def list_folders(path: str) -> List[str]:
    """List folders at the current path."""
    return [
        f for f in os.listdir(path)
        if os.path.isdir(os.path.join(path, f))
    ]


def list_md_files(path: str) -> List[str]:
    """List markdown files at the current path."""
    return [f for f in os.listdir(path) if f.endswith(".md")]


def navigate_to_folder(base_path: str) -> str:
    """Navigate dynamically to the desired folder."""
    current_path = base_path
    while True:
        folders = list_folders(current_path)
        print(f"\n📁 Current Path: {current_path}")
        print("🔹 Enter the **number** corresponding to your choice below:")
        for idx, folder in enumerate(folders, 1):
            print(f" {idx}. {folder}")
        print(f" {len(folders) + 1}. [Create New Subfolder]")
        print(" 0. [Select Current Folder]")

        choice = input("🔢 Enter the number of your choice: ").strip()
        if not choice.isdigit():
            print("⚠️ Please enter a valid number.")
            continue
        choice = int(choice)

        if choice == 0:
            return current_path
        elif choice == len(folders) + 1:
            new_folder = input(
                "📂 Enter new folder name: "
            ).strip()
            new_folder_path = os.path.join(
                current_path, new_folder
            )
            os.makedirs(new_folder_path, exist_ok=True)
            print(f"✅ Created folder: {new_folder_path}")
            current_path = new_folder_path
        elif 1 <= choice <= len(folders):
            current_path = os.path.join(
                current_path, folders[choice - 1]
            )
        else:
            print("⚠️ Invalid choice, please try again.")


def pick_markdown_file(base_path: str) -> str:
    """Navigate dynamically to pick or enter a markdown file."""
    current_path = base_path
    while True:
        folders = list_folders(current_path)
        md_files = list_md_files(current_path)

        print(f"\n📁 Current Path: {current_path}")
        if folders:
            print("📂 Folders:")
            for idx, folder in enumerate(folders, 1):
                print(f" {idx}. {folder}")
        if md_files:
            start_idx = len(folders) + 1
            print("📄 Markdown Files:")
            for idx, file in enumerate(md_files, start_idx):
                print(f" {idx}. {file}")

        print(
            f" {len(folders) + len(md_files) + 1}. "
            "[Manually enter markdown filename]"
        )
        print(" 0. [Go up one folder]")

        choice = input("🔢 Enter the number of your choice: ").strip()
        if not choice.isdigit():
            print("⚠️ Please enter a valid number.")
            continue
        choice = int(choice)

        if choice == 0:
            current_path = os.path.dirname(current_path)
        elif 1 <= choice <= len(folders):
            current_path = os.path.join(
                current_path, folders[choice - 1]
            )
        elif len(folders) < choice <= len(folders) + len(md_files):
            selected_md = md_files[
                choice - len(folders) - 1
            ]
            full_md_path = os.path.join(
                current_path, selected_md
            )
            return full_md_path
        elif choice == len(folders) + len(md_files) + 1:
            manual_name = input(
                "✍️ Enter markdown filename (without .md extension): "
            ).strip()
            if not manual_name:
                print("⚠️ Filename cannot be empty.")
                continue
            full_md_path = os.path.join(
                current_path, f"{manual_name}.md"
            )
            return full_md_path
        else:
            print("⚠️ Invalid choice, please try again.")


def trim_markdown_path(full_md_path: str) -> str:
    """Trim the path to get the correct markdownFilePath string."""
    parts = full_md_path.replace("\\", "/").split("/")

    if "seeds" in parts:
        idx = parts.index("seeds")
        trimmed_parts = parts[idx + 2:]
        trimmed_path = "/".join(trimmed_parts)
        trimmed_path = trimmed_path.rsplit(".md", 1)[0]
        return trimmed_path
    else:
        raise ValueError(
            "⚠️ Path does not contain 'seeds' folder structure."
        )


def prompt_user() -> Tuple[
    str, str, List[Tuple[str, List[str]]], str, dict
]:
    mode = input(
        "📍 Generate directly to project or stage to output? "
        "(project/staging): "
    ).strip().lower()

    base_start_path = os.path.abspath("..")
    base_path = (
        navigate_to_folder(base_start_path)
        if mode == "project"
        else "output"
    )

    print(f"\n📁 Final Destination: {base_path}")
    action = input(
        "🔹 What would you like to do?\n"
        "1. 📄 Create file(s) here\n"
        "2. 📂 Create a new subfolder first\n"
        "Enter 1 or 2: "
    ).strip()

    if action == "2":
        new_subfolder = input(
            "📂 Enter subfolder name: "
        ).strip()
        base_path = os.path.join(base_path, new_subfolder)
        os.makedirs(base_path, exist_ok=True)
        print(f"✅ Created and moved into: {base_path}")

    num_files = int(
        input(
            "🔢 How many files do you want to generate? (1 or more): "
        ).strip()
    )

    folder_map = []
    overrides = {
        "export_names": [],
        "header_texts": [],
        "markdown_paths": []
    }

    for _ in range(num_files):
        file_name = input(
            "📝 Enter filename (without extension): "
        ).strip()

        export_name = input(
            f"🔁 Enter exported component name for {file_name}: "
        ).strip()
        header_text = input(
            f"📝 Enter header text for {file_name}: "
        ).strip()

        print(f"🌐 Select markdown file for {file_name}:")
        markdown_full_path = pick_markdown_file(base_start_path)
        markdown_relative_path = trim_markdown_path(
            markdown_full_path
        )

        folder_map.append((".", [file_name]))

        overrides["export_names"].append(export_name)
        overrides["header_texts"].append(header_text)
        overrides["markdown_paths"].append(markdown_relative_path)

    extension = input(
        "📝 File extension (e.g., tsx, js, py): "
    ).strip().lstrip(".")

    return mode, base_path, folder_map, extension, overrides


def generate_files(
    mode: str,
    base_path: str,
    folder_map: List[Tuple[str, List[str]]],
    extension: str,
    overrides: dict,
):
    os.makedirs(base_path, exist_ok=True)

    export_names = overrides.get("export_names", [])
    header_texts = overrides.get("header_texts", [])
    markdown_paths = overrides.get("markdown_paths", [])

    file_index = 0

    for folder, files in folder_map:
        folder_path = (
            base_path if folder == "."
            else os.path.join(base_path, folder)
        )
        os.makedirs(folder_path, exist_ok=True)

        for name in files:
            file_path = os.path.join(
                folder_path, f"{name}.{extension}"
            )

            if os.path.exists(file_path):
                response = input(
                    f"⚠️ {file_path} exists. Overwrite with template? (y/n): "
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
                extension, export_name, folder,
                header_text, markdown_path
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
                        f"}};\n"
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
            dest = input(
                "📍 Destination path: "
            ).strip()
            for folder, _ in folder_map:
                src = os.path.join(base_path, folder)
                dest_path = os.path.join(dest, folder)
                try:
                    os.makedirs(
                        os.path.dirname(dest_path), exist_ok=True
                    )
                    shutil.copytree(
                        src, dest_path, dirs_exist_ok=True
                    )
                    print(
                        f"📁 Moved '{folder}' to '{dest_path}'"
                    )
                except Exception as e:
                    print(
                        f"❌ Failed to move '{folder}': {e}"
                    )


if __name__ == "__main__":
    mode, base_path, folder_map, extension, overrides = prompt_user()
    generate_files(mode, base_path, folder_map, extension, overrides)
