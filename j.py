Start with a local HTML preview. This lets you check the layout and data without importing clients or sending an email.

1. Create preview_assignment_email.py at the project root:

from pathlib import Path
from jinja2 import Environment, StrictUndefined
# Replace this with your template's actual relative path.
template_path = Path("src/templates/task_assessor_assigned_v1.html")
env = Environment(
    autoescape=True,
    undefined=StrictUndefined,
)
template = env.from_string(
    template_path.read_text(encoding="utf-8")
)
html = template.render(
    initiative_name="Test initiative — Research & Development",
    initiative_id=130,
    initiative_type="New product",
    initiative_url="https://example.invalid/initiative/130/tasks",
    tasks=[
        {
            "task_type": "Assessment",
            "task_name": "Review the initiative",
            "expected_for": "15/10/2026",
        },
        {
            "task_type": "Validation",
            "task_name": "Validate the assessment",
            "expected_for": None,
        },
    ],
)
output = Path("assignment_email_preview.html")
output.write_text(html, encoding="utf-8")
print(f"Preview created: {output.resolve()}")

In VS Code, right-click your template → Copy Relative Path, then use that path in template_path.

2. Run in your activated virtual environment:

python preview_assignment_email.py
open assignment_email_preview.html

3. Check:

* FLOWR logo, green header and readable layout.
* Initiative name, ID and type appear.
* Exactly two task rows appear.
* The second date displays —.
* No raw {{ ... }} appears.

The link uses a dummy address for this preview. This checks the HTML rendering only; the Python helper, template registration and actual email delivery still need a separate test once the clients import issue is resolved.