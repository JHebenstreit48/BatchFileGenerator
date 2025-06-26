from InquirerPy import inquirer
from pathlib import Path
from template_dispatcher import get_template


def select_folder_path(start_path: Path = Path.cwd()) -> str:
    current_path = start_path.resolve()

    while True:
        entries = ["[Up one folder]", "[Create new folder]"]
        subdirs = sorted(
            [f.name for f in current_path.iterdir() if f.is_dir()]
        )
        entries.extend(subdirs)

        choice = inquirer.select(
            message=f"Current folder: {current_path}",
            choices=entries,
            instruction="(Type or use arrows)",
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
        else:
            current_path = current_path / choice

        confirm = inquirer.confirm(
            message=f"Use this folder? {current_path}",
            default=True,
        ).execute()

        if confirm:
            return str(current_path)


def main():
    template_type = "tsx"  # fixed for this script

    component_name = inquirer.text(
        message="Component name:"
    ).execute()

    folder_path = select_folder_path()

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

    output = get_template(
        template_type=template_type,
        component_name=component_name,
        folder_path=folder_path,
        header_text_override=header_text_override,
        markdown_path_override=markdown_path_override,
    )

    output_file = Path(folder_path) / f"{component_name}.tsx"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n✅ File created: {output_file}")


if __name__ == "__main__":
    main()