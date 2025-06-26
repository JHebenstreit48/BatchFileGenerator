from pages_template import tsx_page_template
from routes_templates import nav_topic_template


def get_template(
    template_type: str,
    **kwargs
) -> str:
    if template_type == "tsx":
        return tsx_page_template(**kwargs)
    elif template_type == "nav":
        return nav_topic_template(**kwargs)
    return ""
