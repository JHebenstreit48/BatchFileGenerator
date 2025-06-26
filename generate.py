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
        elif choice == "[Enter markdown filename here]":
            filename = inquirer.text(
                message="Markdown filename (no .md):"
            ).execute()
            if filename:
                full_path = (current_path / filename).resolve()
                parts = full_path.parts

                try:
                    notes_index = parts.index("Notes")
                    # Skip 'Notes' and use the rest of the path
                    trimmed_parts = parts[notes_index + 1:]
                    rel_path = "/".join(trimmed_parts)
                    return rel_path
                except ValueError:
                    print("⚠️ Could not find 'Notes' in path. Please retry.")
                    return navigate_markdown_path(start_path)
        else:
            current_path = current_path / choice


def main():
    template_category = inquirer.select(
        message="What kind of files are you generating?",
        choices=["Pages", "Full Topics Navigation", "Other"],
    ).execute()

    export_mode = inquirer.select(
        message="Export to:",
        choices=["project", "staging"],
    ).execute()

    base_root = (
        Path.cwd().parent
        if export_mode == "project"
        else Path.cwd() / "output"
    )

    print("\n📂 Navigate to export folder destination...")
    export_path = navigate_folders(base_root)

    if template_category == "Pages":
        create_folders = inquirer.confirm(
            message="Create folders before generating files?",
            default=False,
        ).execute()

        if create_folders:
            while True:
                folder_name = inquirer.text(
                    message="Enter folder name (or leave blank to stop):"
                ).execute()
                if not folder_name.strip():
                    break
                new_folder = export_path / folder_name.strip()
                new_folder.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created: {new_folder}")

    multiple = inquirer.confirm(
        message="Generate multiple files?",
        default=True,
    ).execute()

    component_names = []
    markdown_paths = []
    header_texts = []

    if multiple:
        component_names = (
            inquirer.text(message="Enter component names (comma-separated):")
            .execute()
            .split(",")
        )
        component_names = [
            name.strip() for name in component_names if name.strip()
        ]

        if template_category == "Pages":
            for name in component_names:
                print(f"📄 Set markdown file for: {name}")
                md_path = navigate_markdown_path(base_root)
                markdown_paths.append(md_path)
        else:
            markdown_paths = [""] * len(component_names)

        header_texts = (
            inquirer.text(
                message="Enter header texts (comma-separated, same order):"
            )
            .execute()
            .split(",")
        )
        header_texts = [text.strip() for text in header_texts if text.strip()]
    else:
        name = inquirer.text(message="Component name:").execute().strip()
        component_names.append(name)

        if template_category == "Pages":
            print(f"📄 Set markdown file for: {name}")
            markdown_paths.append(navigate_markdown_path(base_root))
        else:
            markdown_paths.append("")

        header = (
            inquirer.text(
                message="Enter header text (optional):"
            ).execute().strip()
        )
        header_texts.append(header)

    for i, component_name in enumerate(component_names):
        folder_path = export_path

        markdown_path = markdown_paths[i] if i < len(markdown_paths) else None
        header_text = header_texts[i] if i < len(header_texts) else None

        template_type = (
            "tsx"
            if template_category == "Pages"
            else (
                "nav" if template_category == "Full Topics Navigation"
                else "tsx"
            )
        )

        output = get_template(
            template_type=template_type,
            component_name=component_name,
            folder_path=str(folder_path),
            header_text_override=header_text,
            markdown_path_override=markdown_path,
        )

        extension = "ts" if template_type == "nav" else "tsx"
        output_file = folder_path / f"{component_name}.{extension}"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"✅ Created: {output_file}")


if __name__ == "__main__":
    main()
