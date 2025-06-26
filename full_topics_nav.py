from InquirerPy import inquirer
from pathlib import Path
from template_dispatcher import get_template


def select_subpages_from_directory() -> tuple[list[str], str]:
    folder = inquirer.text(
        message="Enter path to folder with subpage .ts files:"
    ).execute()

    base_path = Path(folder).resolve()
    ts_files = [f.stem for f in base_path.glob("*.ts")]

    if not ts_files:
        print("⚠️  No .ts files found in that directory.")
        exit()

    selected = inquirer.checkbox(
        message="Select subpages to include:",
        choices=ts_files,
        instruction="(Space to select, Enter to confirm)",
    ).execute()

    return selected, str(base_path).replace("\\", "/")


def select_output_folder(start_path: Path = Path.cwd()) -> str:
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

        elif choice == "[Create multiple folders]":
            while True:
                folder_name = inquirer.text(
                    message="Enter folder name (or leave blank to stop):"
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


def main():
    template_type = "nav"

    topic_name = inquirer.text(
        message="Enter topic name (e.g., HTML, Vue, Go):"
    ).execute()

    subpages, import_base_path = select_subpages_from_directory()

    output_folder = select_output_folder()

    output = get_template(
        template_type=template_type,
        topic_name=topic_name,
        subpages=subpages,
        import_path=import_base_path
    )

    file_path = Path(output_folder) / f"{topic_name}.ts"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"\n✅ Navigation file created: {file_path}")


if __name__ == "__main__":
    main()
