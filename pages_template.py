def tsx_page_template(
    component_name: str,
    header_text: str,
    markdown_path: str
) -> str:
    return (
        f"import PageLayout from '@/Components/NavigationUI/PageLayout';\n"
        f"import Header from '@/Components/Shared/Header';\n"
        f"import Notes from "
        f"'@/Components/PageComponents/Notes/NotesRendering/Notes';\n\n"
        f"const {component_name} = () => {{\n"
        f'    const markdownFilePath = "{markdown_path}";\n\n'
        f"    return (\n"
        f"        <>\n"
        f"            <PageLayout>\n"
        f'            <Header text="{header_text}" />\n'
        f"            <Notes\n"
        f"                filePath={{markdownFilePath}}\n"
        f"            />\n"
        f"            </PageLayout>\n"
        f"        </>\n"
        f"    );\n"
        f"}};\n\n"
        f"export default {component_name};\n"
    )


def get_template(
    template_type: str,
    component_name: str,
    folder_path: str,
    header_text_override: str = None,
    markdown_path_override: str = None,
) -> str:
    if template_type != "tsx":
        return ""

    if markdown_path_override:
        markdown_path = markdown_path_override.lstrip("/\\")
    else:
        markdown_path = folder_path.strip("/\\") + f"/{component_name}.md"

    header_text = header_text_override or component_name.replace("_", " ")

    return tsx_page_template(component_name, header_text, markdown_path)
