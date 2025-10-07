from pathlib import Path
from InquirerPy import inquirer
from template_dispatcher import get_template


# ---------- roots and filters ----------

def _ascend_to(folder_name: str, start: Path) -> Path:
    p = start.resolve()
    while p != p.parent:
        if p.name == folder_name:
            return p
        p = p.parent
    raise RuntimeError(f"Could not find '{folder_name}' above {start}")


def _notes_projects_root() -> Path:
    cb = _ascend_to("CodingBackup", Path.cwd())
    root = cb / "Notes-Projects"
    if not root.is_dir():
        raise RuntimeError(f"Missing folder: {root}")
    return root


def _list_dirs(path: Path) -> list[str]:
    return sorted([f.name for f in path.iterdir() if f.is_dir()])


def _list_project_dirs(path: Path) -> list[str]:
    return sorted([n for n in _list_dirs(path) if n.endswith("-Project")])


def _find_all_api_dirs(notes_projects: Path) -> list[Path]:
    apis = []
    for proj in _list_project_dirs(notes_projects):
        p = notes_projects / proj
        for d in p.iterdir():
            if d.is_dir() and d.name.endswith("-API"):
                apis.append(d)
    return sorted(apis, key=lambda x: x.name.lower())


# ---------- navigation helpers ----------

def navigate_projects(start_path: Path) -> Path:
    current_path = start_path.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Use this folder and generate files]",
        ]
        entries.extend(_list_project_dirs(current_path))

        choice = inquirer.select(
            message=f"Projects root: {current_path}",
            choices=entries,
            instruction="(Arrows / Enter)",
        ).execute()

        if choice == "[Up one folder]":
            if current_path.parent != current_path:
                current_path = current_path.parent
        elif choice == "[Use this folder and generate files]":
            return current_path
        else:
            current_path = current_path / choice


def navigate_folders(start_path: Path) -> Path:
    current_path = start_path.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Create new folder]",
            "[Use this folder and generate files]",
        ]
        entries.extend(_list_dirs(current_path))

        choice = inquirer.select(
            message=f"Current path: {current_path}",
            choices=entries,
            instruction="(Arrows / Enter)",
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


def select_api_repo(notes_projects_root: Path) -> Path:
    apis = _find_all_api_dirs(notes_projects_root)
    if not apis:
        raise RuntimeError("No '*-API' repos found under Notes-Projects.")

    choices = [f"{p.parent.name}/{p.name}" for p in apis]
    pick = inquirer.select(
        message="Select API repo (for markdown):",
        choices=choices,
        instruction="(Arrows / Enter)",
    ).execute()
    idx = choices.index(pick)
    return apis[idx]


def navigate_markdown_in_api(api_root: Path) -> str:
    """
    Jump to api_root/src/seeds/Notes, then let the user drill down or add
    a file. Returns a path relative to 'Notes/...'.
    """
    notes_dir = api_root / "src" / "seeds" / "Notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    current_path = notes_dir.resolve()

    while True:
        entries = [
            "[Up one folder]",
            "[Create new folder]",
            "[Enter markdown filename here]",
        ]
        entries.extend(_list_dirs(current_path))

        choice = inquirer.select(
            message=f"Markdown root: {current_path}",
            choices=entries,
            instruction="(Arrows / Enter)",
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
                full = (current_path / f"{filename}.md").resolve()
                full.parent.mkdir(parents=True, exist_ok=True)
                full.touch(exist_ok=True)
                parts = full.parts
                notes_idx = parts.index("Notes")
                trimmed = parts[notes_idx + 1:]
                return "/".join(trimmed)
        else:
            current_path = current_path / choice


# ---------- main ----------

def main() -> None:
    template_category = inquirer.select(
        message="What kind of files are you generating?",
        choices=["Pages", "Full Topics Navigation", "Other"],
    ).execute()

    export_mode = inquirer.select(
        message="Export to:",
        choices=["project", "staging"],
    ).execute()

    notes_projects = _notes_projects_root()

    if export_mode == "project":
        export_root = notes_projects
    else:
        export_root = Path.cwd().resolve() / "output"

    print("\n📂 Pick a '*-Project' repo, then a destination folder...")
    project_root = navigate_projects(export_root)

    multiple = inquirer.confirm(
        message="Generate multiple files?", default=True
    ).execute()

    component_names = []
    markdown_paths = []
    page_titles = []
    file_destinations = []

    if multiple:
        component_names = inquirer.text(
            message="Enter component names (comma-separated):"
        ).execute().split(",")
        component_names = [n.strip() for n in component_names if n.strip()]

        for name in component_names:
            print(f"\n📁 Select destination for: '{name}'")
            folder = navigate_folders(project_root)
            file_destinations.append(folder)

        if template_category == "Pages":
            api_root = select_api_repo(notes_projects)
            for name in component_names:
                print(f"\n📄 Set markdown path for: {name}")
                md_path = navigate_markdown_in_api(api_root)
                markdown_paths.append(md_path)
        else:
            markdown_paths = [""] * len(component_names)

        page_titles = inquirer.text(
            message=("Enter PageTitle values (comma-separated, optional):")
        ).execute().split(",")
        page_titles = [t.strip() for t in page_titles if t.strip()]

    else:
        name = inquirer.text(message="Component name:").execute().strip()
        component_names.append(name)

        print(f"\n📁 Select destination for: {name}")
        file_destinations.append(navigate_folders(project_root))

        if template_category == "Pages":
            api_root = select_api_repo(notes_projects)
            print(f"\n📄 Set markdown path for: {name}")
            markdown_paths.append(navigate_markdown_in_api(api_root))
        else:
            markdown_paths.append("")

        title = inquirer.text(
            message="Enter PageTitle (optional):"
        ).execute().strip()
        page_titles.append(title)

    for i, name in enumerate(component_names):
        folder_path = file_destinations[i]
        markdown_path = markdown_paths[i] if i < len(markdown_paths) else None
        page_title = page_titles[i] if i < len(page_titles) else None

        template_type = (
            "tsx" if template_category == "Pages"
            else "nav" if template_category == "Full Topics Navigation"
            else "tsx"
        )

        content = get_template(
            template_type=template_type,
            component_name=name,
            folder_path=str(folder_path),
            header_text_override=page_title,
            markdown_path_override=markdown_path,
        )

        ext = "ts" if template_type == "nav" else "tsx"
        output_file = folder_path / f"{name}.{ext}"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"✅ Created: {output_file}")


if __name__ == "__main__":
    main()
