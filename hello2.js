const handleEdit = () => {
  setDateError('');
  setEditedValue(value || '');
  setIsEditing(true);
};

const handleCancel = () => {
  setDateError('');
  setEditedValue(value || '');
  setIsEditing(false);
};

if (isEditing) {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 4,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: 6,
        }}
      >
        <input
          type="date"
          value={editedValue || ''}
          aria-invalid={Boolean(dateError)}
          onChange={event => {
            setEditedValue(event.target.value);
            setDateError('');
          }}
        />

        <IconButton
          hoverColor={BNPColors.ceruleanBlue}
          type="button"
          onClick={handleSave}
        >
          <Icon slug="checked-full" size={16} />
        </IconButton>

        <IconButton
          hoverColor={BNPColors.ceruleanBlue}
          type="button"
          onClick={handleCancel}
        >
          <Icon slug="close" size={16} />
        </IconButton>
      </div>

      {dateError && (
        <span
          role="alert"
          style={{
            color: 'red',
            fontSize: 12,
            whiteSpace: 'normal',
            textAlign: 'center',
          }}
        >
          {dateError}
        </span>
      )}
    </div>
  );
}