 <textarea
  readOnly
  value={JSON.stringify(
    {
      displayedDate: value,
      editedValue,
      original,
    },
    null,
    2,
  )}
  onFocus={event => event.target.select()}
  style={{ width: 400, height: 180 }}
/>