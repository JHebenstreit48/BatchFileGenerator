from InquirerPy import inquirer
from pathlib import Path
from template_dispatcher import get_template


def select_folder_path(start_path: Path) -> str:
    current_path = start_path.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Create new folder]",
            "[Create multiple folders]",
            "[Enter full nested path]"
        ]

        subdirs = sorted(
            [f.name for f in current_path.iterdir() if f.is_dir()]
        )
        entries.extend(subdirs)

        choice = inquirer.select(
            message=f"Current folder: {current_path}",
            choices=entries,
            instruction="(Use arrow keys)",
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

        elif choice == "[Create multiple folders]":
            while True:
                folder_name = inquirer.text(
                    message="Enter folder name "
                            "(or leave blank to stop):"
                ).execute()
                if not folder_name.strip():
                    break
                new_folder = current_path / folder_name
                new_folder.mkdir(parents=True, exist_ok=True)

        elif choice == "[Enter full nested path]":
            full_path = inquirer.text(
                message="Enter full nested path from here:"
            ).execute()
            new_path = current_path / full_path
            new_path.mkdir(parents=True, exist_ok=True)
            current_path = new_path

        else:
            current_path = current_path / choice

        confirm = inquirer.confirm(
            message=f"Use this folder? {current_path}",
            default=True,
        ).execute()

        if confirm:
            return str(current_path)


def select_existing_folder(start_path: Path) -> str:
    current_path = start_path.resolve()

    while True:
        subdirs = sorted(
            [f.name for f in current_path.iterdir() if f.is_dir()]
        )
        entries = ["[Up one folder]"] + subdirs

        choice = inquirer.select(
            message=(
                f"Navigate to export folder:\n"
                f"Current path: {current_path}"
            ),
            choices=entries,
            instruction="(Arrow keys)",
        ).execute()

        if choice == "[Up one folder]":
            if current_path.parent != current_path:
                current_path = current_path.parent
        else:
            current_path = current_path / choice

        confirm = inquirer.confirm(
            message=f"Use this folder? {current_path}",
            default=True,
        ).execute()

        if confirm:
            return str(current_path)


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
    base_output_path = Path(
        select_existing_folder(start_path=base_root)
    )

    multiple = inquirer.confirm(
        message="Generate multiple files?", default=True
    ).execute()

    component_names = []
    if multiple:
        while True:
            name = inquirer.text(
                message="Component name (leave blank to stop):"
            ).execute()
            if not name.strip():
                break
            component_names.append(name.strip())
    else:
        name = inquirer.text(message="Component name:").execute()
        component_names.append(name.strip())

    for component_name in component_names:
        folder_path = select_folder_path(
            start_path=base_output_path
        )

        markdown_path_override = None
        if inquirer.confirm(
            message="Override markdown path?", default=False
        ).execute():
            markdown_path_override = inquirer.text(
                message="Enter custom markdown path:"
            ).execute()

        header_text_override = None
        if inquirer.confirm(
            message="Override header text?", default=False
        ).execute():
            header_text_override = inquirer.text(
                message="Enter custom header text:"
            ).execute()

        if template_category == "Pages":
            template_type = "tsx"
        elif template_category == "Full Topics Navigation":
            template_type = "nav"
        else:
            template_type = "tsx"

        output = get_template(
            template_type=template_type,
            component_name=component_name,
            folder_path=folder_path,
            header_text_override=header_text_override,
            markdown_path_override=markdown_path_override,
        )

        output_file = Path(folder_path) / (
            f"{component_name}.{template_type}"
        )
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(output)

        print(f"✅ Created: {output_file}")


if __name__ == "__main__":

    main()
