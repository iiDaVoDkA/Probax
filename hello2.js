const {
  committeeIdentifierToCreate,
  ...initiativePipeline
} = action.values;

const initiativeId = initiativePipeline.id;

if (committeeIdentifierToCreate) {
  yield call(
    authenticatedCall,
    postCommitteeIdentifier,
    initiativeId,
    committeeIdentifierToCreate,
  );
}

const handleSave = event => {
  event.preventDefault();
  event.stopPropagation();

  const committeeId = original.__committeeId;
  const previousValue = value == null ? '' : String(value);

  if (editedValue === previousValue) {
    setIsEditing(false);
    return;
  }

  updateInitiative(original.id, {
    id: original.id,

    committeeIdentifiers: {
      ...original.committeeIdentifiers,
      [committeeId]: editedValue,
    },

    committeeIdentifierToCreate:
      previousValue === ''
        ? {
            commitee_id: Number(committeeId),
            commitee_initiative_identifier: editedValue,
          }
        : undefined,

    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};


<input
  type="text"
  value={editedValue}
  size={1}
  style={{
    width: 80,
    minWidth: 0,
    height: 24,
    padding: '2px 4px',
    boxSizing: 'border-box',
    fontFamily: 'inherit',
    fontSize: 12,
    fontWeight: 400,
    lineHeight: '16px',
  }}
  onClick={event => event.stopPropagation()}
  onChange={event => setEditedValue(event.target.value)}
/>
