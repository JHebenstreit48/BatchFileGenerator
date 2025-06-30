from pathlib import Path
from InquirerPy import inquirer
from template_dispatcher import get_template


def navigate_folders(start_path: Path) -> Path:
    current_path = start_path.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Create new folder]",
            "[Use this folder and generate files]",
        ]

        subdirs = sorted(
            [f.name for f in current_path.iterdir() if f.is_dir()]
        )
        entries.extend(subdirs)

        choice = inquirer.select(
            message=f"Current path: {current_path}",
            choices=entries,
            instruction="(Arrow keys to browse, Enter to select)",
        ).execute()

        if choice == "[Up one folder]":
            if current_path.parent != current_path:
                current_path = current_path.parent
        elif choice == "[Create new folder]":
            new_name = inquirer.text(
                message="Enter new folder name:"
            ).execute()
            new_folder = current_path / new_name
            new_folder.mkdir(parents=True, exist_ok=True)
            print(f"📁 Folder '{new_name}' created!")
            print("➡ Select '[Use this folder and generate files]'")
            current_path = new_folder
        elif choice == "[Use this folder and generate files]":
            return current_path
        else:
            current_path = current_path / choice


def navigate_markdown_path(start_path: Path) -> str:
    current_path = start_path.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Create new folder]",
            "[Enter markdown filename here]",
        ]

        folders = sorted(
            [f.name for f in current_path.iterdir() if f.is_dir()]
        )
        entries.extend(folders)

        choice = inquirer.select(
            message=f"Navigate to markdown file folder: {current_path}",
            choices=entries,
            instruction="(Arrow keys to browse, Enter to select)",
        ).execute()

        if choice == "[Up one folder]":
            if current_path.parent != current_path:
                current_path = current_path.parent
        elif choice == "[Create new folder]":
            new_name = inquirer.text(
                message="Enter new folder name:"
            ).execute()
            new_folder = current_path / new_name
            new_folder.mkdir(parents=True, exist_ok=True)
            print(f"📁 Folder '{new_name}' created!")
            current_path = new_folder
        elif choice == "[Enter markdown filename here]":
            filename = inquirer.text(
                message="Markdown filename (no .md):"
            ).execute()
            if filename:
                full_path = (current_path / f"{filename}.md").resolve()
                full_path.parent.mkdir(parents=True, exist_ok=True)
                full_path.touch(exist_ok=True)
                parts = full_path.parts
                try:
                    notes_index = parts.index("Notes")
                    trimmed = parts[notes_index + 1:]
                    return "/".join(trimmed)
                except ValueError:
                    print("⚠️ 'Notes' folder not found in path.")
                    return navigate_markdown_path(start_path)
        else:
            current_path = current_path / choice


def main() -> None:
    template_category = inquirer.select(
        message="What kind of files are you generating?",
        choices=["Pages", "Full Topics Navigation", "Other"],
    ).execute()

    export_mode = inquirer.select(
        message="Export to:",
        choices=["project", "staging"],
    ).execute()

    root_path = Path.cwd().resolve()
    if export_mode == "project":
        coding_backup_path = root_path.parents[1]
    else:
        coding_backup_path = root_path / "output"

    print("\n📂 Navigate to export folder destination...")
    export_path = navigate_folders(coding_backup_path)

    multiple = inquirer.confirm(
        message="Generate multiple files?", default=True
    ).execute()

    component_names = []
    markdown_paths = []
    header_texts = []
    file_destinations = []

    if multiple:
        component_names = inquirer.text(
            message="Enter component names (comma-separated):"
        ).execute().split(",")

        component_names = [
            name.strip() for name in component_names if name.strip()
        ]

        for name in component_names:
            print(f"\n📁 Select folder for: '{name}'")
            folder = navigate_folders(export_path)
            file_destinations.append(folder)

        if template_category == "Pages":
            for name in component_names:
                print(f"\n📄 Set markdown path for: {name}")
                md_path = navigate_markdown_path(coding_backup_path)
                markdown_paths.append(md_path)
        else:
            markdown_paths = [""] * len(component_names)

        header_texts = inquirer.text(
            message="Enter header texts (comma-separated):"
        ).execute().split(",")

        header_texts = [
            text.strip() for text in header_texts if text.strip()
        ]
    else:
        name = inquirer.text(message="Component name:").execute().strip()
        component_names.append(name)

        print(f"\n📁 Select folder for: {name}")
        file_destinations.append(navigate_folders(export_path))

        if template_category == "Pages":
            print(f"\n📄 Set markdown path for: {name}")
            markdown_paths.append(
                navigate_markdown_path(coding_backup_path)
            )
        else:
            markdown_paths.append("")

        header = inquirer.text(
            message="Enter header text (optional):"
        ).execute().strip()
        header_texts.append(header)

    for i, name in enumerate(component_names):
        folder_path = file_destinations[i]
        markdown_path = (
            markdown_paths[i] if i < len(markdown_paths) else None
        )
        header_text = (
            header_texts[i] if i < len(header_texts) else None
        )

        template_type = (
            "tsx" if template_category == "Pages"
            else "nav" if template_category == "Full Topics Navigation"
            else "tsx"
        )

        content = get_template(
            template_type=template_type,
            component_name=name,
            folder_path=str(folder_path),
            header_text_override=header_text,
            markdown_path_override=markdown_path,
        )

        ext = "ts" if template_type == "nav" else "tsx"
        output_file = folder_path / f"{name}.{ext}"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Created: {output_file}")


if __name__ == "__main__":
    main()
