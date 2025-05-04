import os
import shutil


def prompt_user():
    sections = input(
        (
            "📁 Enter one or more nested folder paths (comma-separated, "
            "e.g., Shared/Utils, Features/Auth): "
        )
    ).split(",")
    sections = [s.strip() for s in sections if s.strip()]

    extension = (
        input(
            "📄 Enter the file extension (e.g., tsx, js, py): "
        ).strip().lstrip(".")
    )

    filenames = input(
        "📝 Enter filenames (comma-separated, no extension): "
    ).split(",")
    filenames = [name.strip() for name in filenames if name.strip()]

    return sections, extension, filenames


def generate_files(sections: list[str], extension: str, filenames: list[str]):
    base_output = "output"
    os.makedirs(base_output, exist_ok=True)

    for section in sections:
        section_path = os.path.join(base_output, section)
        os.makedirs(section_path, exist_ok=True)

        for name in filenames:
            file_path = os.path.join(section_path, f"{name}.{extension}")
            with open(file_path, "w") as f:
                f.write(
                    f"// Auto-generated {extension.upper()} file: {name}\n\n"
                )

                if extension == "tsx":
                    f.write(
                        f"export default function {name}() {{\n"
                        f"  return (\n"
                        f"    <div>\n"
                        f"      <h1>{name}</h1>\n"
                        f"    </div>\n"
                        f"  );\n"
                        f"}}\n"
                    )
                elif extension in ["js", "ts"]:
                    f.write(
                        f"export const {name} = () => {{\n"
                        f"  console.log('{name} loaded');\n"
                        f"}};\n"
                    )
                elif extension == "py":
                    f.write(
                        f"def {name.lower()}():\n"
                        f"    print('{name} function')\n"
                    )
                else:
                    f.write(f"// {name}.{extension} - customize as needed\n")

            print(f"✅ Created: {file_path}")


def move_to_project(sections: list[str]):
    move = input(
        "🚚 Move generated folders to another project? (y/n): "
    ).lower()
    if move != "y":
        return

    destination = input("📍 Enter the full destination path: ").strip()

    for section in sections:
        src = os.path.join("output", section)
        dest = os.path.join(destination, section)

        try:
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copytree(src, dest, dirs_exist_ok=True)
            print(f"📁 Moved '{section}' to '{dest}'")
        except Exception as e:
            print(f"❌ Failed to move '{section}': {e}")


if __name__ == "__main__":
    sections, extension, filenames = prompt_user()
    generate_files(sections, extension, filenames)
    move_to_project(sections)
