
I would not put the new PATCH logic in initiativePipeline just because there is already a getTemplate() there.

For this ticket, the cleanest fit with the architecture you showed is:

Backend
resources/template/template.py
        ↑
        │ PATCH /templates/{id}
        │
Frontend
redux/entities/templateInitiative/
    api.js
    constants.js
    actions.js
    sagas.js
        ↑
TemplateInitiative.wrap.js
        ↑
TemplateInitiative.js

That keeps all the functionality used by the TemplateInitiative administration page together.

The getTemplate() you found under initiativePipeline / initiativeTasks is there because those other features need to read a template. It doesn’t mean that module should own template administration.

So I would do this.

1. Backend: resources/template/template.py

You already have:

class TemplateResource(Resource):

and the route supports /templates/{id}, because GET /templates/{id} already exists.

Add a PATCH underneath get.

You can actually make the ADMIN restriction cleaner than what we previously did, because this file already uses authorized_plm_roles:

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

So you don’t need to manually calculate:

is_admin = ...

The decorator already handles authorization.

And remove the special template_name ADMIN code we added to TemplateConfigResource.patch.

⸻

2. Put the frontend API in templateInitiative/api.js

Even though it calls /templates, I would place it beside the API calls used by this page:

export function patchTemplateById(
  templateId: string,
  payload: any,
  token: string,
) {
  const requestURL = `${config.INITIATIVE_API_URL}/templates/${templateId}`;
  return request(requestURL, {
    method: 'PATCH',
    headers: {
      authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    data: payload,
  });
}

Don’t modify the getTemplate() sitting in initiativeTasks or initiativePipeline.

⸻

3. templateInitiative/constants.js

Add:

export const PATCH_TEMPLATE_REQUEST =
  'app/templateInitiative/PATCH_TEMPLATE_REQUEST';
export const PATCH_TEMPLATE_SUCCESS =
  'app/templateInitiative/PATCH_TEMPLATE_SUCCESS';
export const PATCH_TEMPLATE_FAILURE =
  'app/templateInitiative/PATCH_TEMPLATE_FAILURE';

Use whatever naming prefix that file already uses; just mirror its existing constants.

⸻

4. templateInitiative/actions.js

At the top, import those three constants.

Then add:

export const patchTemplate = (
  templateId: string,
  values: any,
) => ({
  type: PATCH_TEMPLATE_REQUEST,
  payload: {
    templateId,
    values,
  },
});
export const patchTemplateSuccess = template => ({
  type: PATCH_TEMPLATE_SUCCESS,
  payload: {
    template,
  },
});
export const patchTemplateFailure = error => ({
  type: PATCH_TEMPLATE_FAILURE,
  error,
});

And if this file has the big:

export default {
   ...
}

at the bottom, add:

patchTemplate,
patchTemplateSuccess,
patchTemplateFailure,

there too.

⸻

5. templateInitiative/sagas.js

Add the API import:

import {
  ...
  patchTemplateById,
} from './api';

Add the actions:

import {
  ...
  patchTemplateSuccess,
  patchTemplateFailure,
  getTemplateConfig,
} from './actions';

Add the constant:

import {
  ...
  PATCH_TEMPLATE_REQUEST,
} from './constants';

Then add:

export function* patchTemplateSaga(action: any): Saga<> {
  try {
    const { templateId, values } = action.payload;
    const response = yield authenticatedCall(
      patchTemplateById,
      templateId,
      values,
    );
    yield put(patchTemplateSuccess(response.data));
    // Important because this screen displays templates-config
    yield put(getTemplateConfig());
  } catch (err) {
    yield put(patchTemplateFailure(err));
  }
}

And in the bottom watcher:

export default function* sagas(): Saga<> {

add:

yield takeLatest(
  PATCH_TEMPLATE_REQUEST,
  patchTemplateSaga,
);

The reason for:

yield put(getTemplateConfig());

is exactly what you were confused about earlier.

The write goes to:

/templates/3

but this page’s display data comes from:

/templates-config

So after renaming the actual Template, we reload template-config and the screen receives the new template_name.

⸻

6. TemplateInitiative.wrap.js

You currently import:

getTemplateConfig,
patchTemplateConfig,
deleteTemplateConfig,
createTemplateConfig,

Add:

patchTemplate,

So:

import {
  getTemplateConfig,
  patchTemplateConfig,
  deleteTemplateConfig,
  createTemplateConfig,
  patchTemplate,
} from '@app/redux/entities/templateInitiative/actions';

Then add to mapDispatchToProps:

patchTemplate: (id, values) =>
  dispatch(patchTemplate(id, values)),

You should then have something like:

const mapDispatchToProps = dispatch => ({
  fetchAllTeams: () => dispatch(fetchAllTeams()),
  fetchUsers: () => dispatch(fetchUsers()),
  fetchTeams: () => dispatch(fetchTeams()),
  getTemplateConfig: () =>
    dispatch(getTemplateConfig()),
  getAssessmentCategory: () =>
    dispatch(getAssessmentCategory()),
  createTemplateConfig: payload =>
    dispatch(createTemplateConfig(payload)),
  patchTemplateConfig: (id, values) =>
    dispatch(patchTemplateConfig(id, values)),
  patchTemplate: (id, values) =>
    dispatch(patchTemplate(id, values)),
  deleteTemplateConfig: id =>
    dispatch(deleteTemplateConfig(id)),
  fetchProducts: () => dispatch(fetchProducts()),
}));

⸻

7. Finally TemplateInitiative.js

Get:

patchTemplate,

from props.

Then your save becomes very small:

const saveTemplateEdit = useCallback(
  (oldName, rows) => {
    const newName = templateNameDraft.trim();
    if (!newName || newName === oldName) {
      cancelTemplateEdit();
      return;
    }
    patchTemplate(rows[0].template_id, {
      name: newName,
    });
    setEditingTemplateName(null);
    setTemplateNameDraft('');
  },
  [
    templateNameDraft,
    patchTemplate,
    cancelTemplateEdit,
  ],
);

And your calls remain:

saveTemplateEdit(templateName, rows);

The architecture then makes sense

TemplateInitiative page
        │
        │ Displays
        ▼
GET /templates-config
        │
        │ Gives:
        │ id = config ID
        │ template_id = template ID
        │ template_name
        │
        ▼
User clicks ✏️
        │
        ▼
patchTemplate(template_id, { name })
        │
        ▼
Redux action
        │
        ▼
templateInitiative saga
        │
        ▼
PATCH /templates/{template_id}
        │
        ▼
Template.name changes
SAME template_id
        │
        ▼
GET /templates-config again
        │
        ▼
UI receives updated template_name

So yes: put the new action/saga/API under templateInitiative, not under initiativePipeline.

The rule I’d use here is: where is the operation initiated and managed? In this case it is an admin operation on the TemplateInitiative page, so that Redux module should own the flow. The backend resource, however, correctly belongs to TemplateResource because the actual entity being modified is the Template.