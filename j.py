Cell: (props: any) => (
  <CommitteeDateCell
    key={`committee-date-${props.original.id}`}
    original={props.original}
    value={props.value}
  />
),


const CommitteeDateCellComponent = ({
  original,
  value,
  updateInitiative,
}: any) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editedValue, setEditedValue] = React.useState(value || '');

  const handleEdit = () => {
    setEditedValue(value || '');
    setIsEditing(true);
  };

  const handleCancel = () => {
    setEditedValue(value || '');
    setIsEditing(false);
  };

  const handleSave = () => {
    updateInitiative(original.id, {
      committeeDate: editedValue,
      id: original.id,
    });

    setIsEditing(false);
  };

  if (isEditing) {
    return (
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
          onChange={event => setEditedValue(event.target.value)}
        />

        <button type="button" onClick={handleSave}>
          ✓
        </button>

        <button type="button" onClick={handleCancel}>
          ✕
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 6,
      }}
    >
      <span>{value || '-'}</span>

      <button type="button" onClick={handleEdit}>
        ✎
      </button>
    </div>
  );
};