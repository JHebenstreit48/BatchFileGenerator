def tsx_page_template(
    component_name: str, header_text: str, markdown_path: str
) -> str:
    return (
        f'import Header from "@/Components/Shared/Header";\n'
        f'import Notes from "@/Components/PageComponents/Notes/'
        f'NotesRender";\n\n'
        f"const {component_name} = () => {{\n"
        f'    const markdownFilePath = "{markdown_path}";\n\n'
        f"    return (\n"
        f"        <>\n"
        f'            <Header text="{header_text}" />\n'
        f"            <Notes\n"
        f"                filePath={{markdownFilePath}}\n"
        f'                markdownContent="markdownContent"\n'
        f"            />\n"
        f"        </>\n"
        f"    );\n"
        f"}};\n\n"
        f"export default {component_name};\n"
    )


def get_template(
    extension: str,
    component_name: str,
    folder_path: str,
    header_text_override: str = None,
    markdown_path_override: str = None
) -> str:
    if extension != "tsx":
        return ""

    # Determine fallback markdown path
    if markdown_path_override:
        markdown_path = markdown_path_override.lstrip("/\\")
    else:
        markdown_path = folder_path.strip("/\\") + f"/{component_name}.md"

    # Determine fallback header text
    header_text = header_text_override or component_name.replace("_", " ")

    return tsx_page_template(component_name, header_text, markdown_path)
