from typing import Optional


def _prettify(name: str) -> str:
    return name.replace("_", " ")


def tsx_page_template(
    component_name: str,
    page_title: str,
    markdown_path: str,
) -> str:
    """
    Generate a .tsx page with:
      - PageLayout + Header + PageTitle + Notes
      - Notes receives a path string (no .md extension required)
    """
    return (
        "import PageLayout from "
        "'@/Components/NavigationUI/PageLayout';\n"
        "import Header from "
        "'@/Components/Shared/Header/Header';\n"
        "import PageTitle from "
        "'@/Components/PageComponents/PageTitle';\n"
        "import Notes from "
        "'@/Components/PageComponents/Notes/Notes';\n\n"
        f"const {component_name} = () => {{\n"
        f"  const markdownFilePath = '{markdown_path}';\n\n"
        "  return (\n"
        "    <>\n"
        "      <PageLayout>\n"
        "        <Header />\n"
        f"        <PageTitle title=\"{page_title}\" />\n"
        "        <Notes filePath={markdownFilePath} />\n"
        "      </PageLayout>\n"
        "    </>\n"
        "  );\n"
        "};\n\n"
        f"export default {component_name};\n"
    )


def _clean_path(path: str) -> str:
    # Strip leading slashes/backslashes; drop trailing ".md".
    p = path.lstrip("/\\")
    if p.lower().endswith(".md"):
        p = p[:-3]
    return p


def get_template(
    template_type: str,
    component_name: str,
    folder_path: str,
    header_text_override: Optional[str] = None,
    markdown_path_override: Optional[str] = None,
) -> str:
    """
    template_type: 'tsx' (others return '')
    component_name: React component name (e.g., 'CLI')
    folder_path: base path to markdown
    overrides: optional page title and/or explicit markdown path
    """
    if template_type != "tsx":
        return ""

    if markdown_path_override:
        markdown_path = _clean_path(markdown_path_override)
    else:
        base = folder_path.strip("/\\")
        markdown_path = _clean_path(f"{base}/{component_name}")

    page_title = header_text_override or _prettify(component_name)

    return tsx_page_template(component_name, page_title, markdown_path)
