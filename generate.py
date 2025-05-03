import os


def prompt_user():
    section = input(
        "📁 Enter the section/folder name (e.g., UnitTesting): "
    ).strip()

    extension = input(
        "📄 Enter the file extension (e.g., tsx, js, py): "
    ).strip().lstrip(".")

    filenames = input(
        "📝 Enter filenames (comma-separated, no extension): "
    ).split(",")

    filenames = [name.strip() for name in filenames if name.strip()]
    return section, extension, filenames


def generate_files(section: str, extension: str, filenames: list[str]):
    base_path = os.path.join("output", section)
    os.makedirs(base_path, exist_ok=True)

    for name in filenames:
        file_path = os.path.join(base_path, f"{name}.{extension}")
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


if __name__ == "__main__":
    section, extension, filenames = prompt_user()
    generate_files(section, extension, filenames)
