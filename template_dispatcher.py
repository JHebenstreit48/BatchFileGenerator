from pages_template import tsx_page_template


def nav_topic_template(
    topic_name: str,
    subpages: list[str],
    import_path: str
) -> str:
    const_name = f"{topic_name}Nav"
    normalized_path = import_path.replace("\\", "/")

    imports = [
        "import { Subpage } from "
        "'@/Navigation/CombinedNav/CombinedNavAndTypes/NavigationTypes';\n"
    ]

    for subpage in subpages:
        imports.append(
            f"import {subpage} from "
            f"'@/{normalized_path}/{subpage}';"
        )

    subpage_list = ",\n    ".join(subpages)

    output = (
        "\n".join(imports)
        + "\n\n"
        + f"const {const_name}: Subpage = {{\n"
        + f"  name: '{topic_name}',\n"
        + f"  subpages: [\n    {subpage_list}\n  ]\n"
        + "};\n\n"
        + f"export default {const_name};\n"
    )

    return output


def get_template(
    template_type: str,
    **kwargs
) -> str:
    if template_type == "tsx":
        component_name = kwargs["component_name"]
        header_text = (
            kwargs.get("header_text_override")
            or component_name.replace("_", " ")
        )
        markdown_path = kwargs.get("markdown_path_override", "").lstrip("/\\")
        return tsx_page_template(
            component_name=component_name,
            header_text=header_text,
            markdown_path=markdown_path
        )

    elif template_type == "nav":
        return nav_topic_template(**kwargs)

    return ""
