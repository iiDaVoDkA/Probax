You’re close, but the saveTemplateEdit you added is currently wrong because it still reuses the old draft from saveEdit.

Your existing saveEdit above shows us the real signature used in this app:

patchTemplateConfig(row.id, {
  ...
});

So keep saveEdit exactly as it is. Replace only your new saveTemplateEdit with this:

const saveTemplateEdit = useCallback(
  (oldName, rows) => {
    const newName = templateNameDraft.trim();
    if (!newName || newName === oldName) {
      cancelTemplateEdit();
      return;
    }
    rows.forEach(row => {
      patchTemplateConfig(row.id, {
        template_name: newName,
      });
    });
    setEditingTemplateName(null);
    setTemplateNameDraft("");
  },
  [templateNameDraft, patchTemplateConfig, cancelTemplateEdit],
);

Why yours is wrong now

You currently have something like:

const saveTemplateEdit = useCallback(
  row => {
    if (!draft) return;
    patchTemplateConfig(row.id, {
      template_name: draft.template_name,
    });

But this new template-name editor does not use:

draft

It uses:

templateNameDraft

These two systems are separate:

Existing row edit:
draft
editingId
saveEdit(row)
New template-name edit:
templateNameDraft
editingTemplateName
saveTemplateEdit(oldName, rows)

Don’t mix them.

Then in the JSX, your save button must call:

saveTemplateEdit(templateName, rows)

For example:

<IconButton
  onClick={e => {
    e.stopPropagation();
    saveTemplateEdit(templateName, rows);
  }}
>
  <Icon slug="checked-full" size={16} />
</IconButton>

And Enter:

onKeyDown={e => {
  if (e.key === "Enter") {
    saveTemplateEdit(templateName, rows);
  }
  if (e.key === "Escape") {
    cancelTemplateEdit();
  }
}}

So after the correction your code around lines 330–353 should essentially be:

const startTemplateEdit = useCallback(name => {
  setEditingTemplateName(name);
  setTemplateNameDraft(name);
}, []);
const cancelTemplateEdit = useCallback(() => {
  setEditingTemplateName(null);
  setTemplateNameDraft("");
}, []);
const saveTemplateEdit = useCallback(
  (oldName, rows) => {
    const newName = templateNameDraft.trim();
    if (!newName || newName === oldName) {
      cancelTemplateEdit();
      return;
    }
    rows.forEach(row => {
      patchTemplateConfig(row.id, {
        template_name: newName,
      });
    });
    setEditingTemplateName(null);
    setTemplateNameDraft("");
  },
  [templateNameDraft, patchTemplateConfig, cancelTemplateEdit],
);

That matches the actual patchTemplateConfig(row.id, payload) pattern already used by FLOWR in the code immediately above.