<Dropdown
  options={teamOptions}
  value={
    teamOptions.find(
      o => String(o.value) === String(draft?.team_id)
    ) || null
  }
  onChange={option =>
    updateDraft("team_id", option?.value ?? "")
  }
  isClearable={false}
  isSearchable
  style={{ width: widthColumns[3] - widthColumns[5] }}
/>