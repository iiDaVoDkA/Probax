<NewTextArea
  value={inlineDraft.description || ""}
  onChange={e =>
    updateInlineDraft(
      original.template_name,
      "description",
      e.target.value
    )
  }
  placeholder="Description"
/>

<NewTextArea
  value={draft?.description ?? ""}
  onChange={e =>
    updateDraft("description", e.target.value)
  }
  placeholder="Description"
/>
import { NewTextArea } from "@component-studio/ui";
