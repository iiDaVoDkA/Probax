<Dropdown
  options={teamOptions}
  value={
    teamOptions.find(
      o => String(o.value) === String(inlineDraft?.team_id)
    ) || null
  }
  onChange={option =>
    updateInlineDraft(
      original.template_name,
      "team_id",
      option?.value ?? ""
    )
  }
  isClearable={false}
  isSearchable
  style={{ width: "100%" }}
/>