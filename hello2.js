Exactly. Your screenshots confirm it: TemplateResource currently only has GET, and the frontend only has getTemplate(...). There is no existing PATCH for a Template.

So for this ticket, we actually do need to add a small PATCH flow. We should stop trying to reuse patchTemplateConfig, because that is what caused the strange “new template” behavior.

The clean solution is:

TemplateInitiative
      ↓
GET /templates-config        ← keep this, page needs the rows
      ↓
user edits heading
      ↓
PATCH /templates/{template_id}   ← NEW
{ name: "New name" }
      ↓
same template ID, new name
      ↓
refresh /templates-config

1. Backend — resources/template/template.py

Your file already has:

class TemplateResource(Resource):

and:

def get(user, id=None):

Add this under the GET:

@staticmethod
@authorized_plm_roles(
    [
        "ADMIN",
    ]
)
def patch(user, id=None):
    payload = request.get_json()
    if not id:
        return {"message": "Missing template id"}, 400
    if not payload:
        return {"message": "Missing JSON payload"}, 400
    name = str(payload.get("name", "")).strip()
    if not name:
        return {"message": "Template name cannot be empty"}, 400
    template = TemplateRepository.get_by_template_id(id)
    if not template:
        return {"message": f"Template with id {id} not found"}, 404
    try:
        template.name = name
        db.session.commit()
        return template.to_json(), 200
    except Exception as exc:
        db.session.rollback()
        return {"message": str(exc)}, 400

This is much cleaner than the ADMIN code we had put inside TemplateConfigResource.

And importantly:

template id = 3
name = Testing

becomes:

template id = 3
name = New Testing

No id 4 gets created.

Remove the special:

if "template_name" in payload:
    ...

code that we added to TemplateConfigResource.patch for this ticket. That resource should go back to its previous behavior.

⸻

2. Frontend API — add PATCH beside the template API

You showed an existing:

export function getTemplate(templateId, token: string) {
  const requestURL =
    `${config.INITIATIVE_API_URL}/templates/${templateId}`;
  return request(requestURL, {
    method: 'GET',
    headers: {
      authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });
}

Add underneath:

export function patchTemplateById(
  templateId: string,
  payload: any,
  token: string,
) {
  const requestURL =
    `${config.INITIATIVE_API_URL}/templates/${templateId}`;
  return request(requestURL, {
    method: 'PATCH',
    headers: {
      authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    data: payload,
  });
}

That’s your new API call.

⸻

3. Do NOT use this anymore for renaming

Remove this approach:

rows.forEach(row => {
  patchTemplateConfig(row.id, {
    template_name: newName,
  });
});

That was PATCHing:

/templates-config/{config_id}

which is the wrong entity.

Instead we’ll eventually call:

patchTemplate(rows[0].template_id, {
  name: newName,
});

Only one PATCH.

⸻

4. Why rows[0].template_id is correct

Your Network screenshot shows:

{
  id: 1,             // config ID
  template_id: 3,    // template ID
  template_name: "Testingi",
  ...
}

So:

row.id

means:

config row

whereas:

row.template_id

means:

actual template

For this ticket we need the second one.

⸻

5. We still need Redux/Saga wiring

Since your application uses Redux Saga, we shouldn’t call patchTemplateById() directly from the component.

We need the normal FLOWR path:

TemplateInitiative.js
       ↓
patchTemplate(...)
       ↓
action
       ↓
saga
       ↓
patchTemplateById(...)
       ↓
PATCH /templates/{id}
       ↓
refresh template-config

You already showed me templateInitiative/sagas.js, so we’ll follow its existing pattern rather than invent something different.

Don’t add more code yet.

Show me these two files:

src/redux/entities/templateInitiative/actions.js

and:

TemplateInitiative.wrap.js

Then I can give you the exact additions for each file, line by line, and we’ll have the clean minimal implementation.