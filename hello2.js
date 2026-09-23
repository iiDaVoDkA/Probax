
<input
  type="date"
  value={editedValue || ''}
  aria-invalid={Boolean(dateError)}
  style={{
    fontSize: 14,
    fontFamily: 'inherit',
    fontWeight: 400,
    width: 125,
    height: 26,
    padding: '2px 4px',
    boxSizing: 'border-box',
  }}
  onChange={event => {
    setEditedValue(event.target.value);
    setDateError('');
  }}
/>