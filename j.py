const CommitteeIdCellComponent = ({
  original,
  value,
  updateInitiative,
}: any) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editedValue, setEditedValue] = React.useState(value || '');

  const handleEdit = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setEditedValue(value || '');
    setIsEditing(true);
  };

  const handleCancel = (event) => {
    event.preventDefault();
    event.stopPropagation();

    setEditedValue(value || '');
    setIsEditing(false);
  };

  const handleSave = (event) => {
    event.preventDefault();
    event.stopPropagation();

    updateInitiative(original.id, {
      id: original.id,

      // IMPORTANT:
      // verify that this is the REAL writable backend field
      committeeIdentifier: editedValue,
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
        onClick={(event) => event.stopPropagation()}
      >
        <input
          type="text"
          value={editedValue}
          onClick={(event) => event.stopPropagation()}
          onChange={(event) => setEditedValue(event.target.value)}
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
      onClick={(event) => event.stopPropagation()}
    >
      <span>{value || '-'}</span>

      <button type="button" onClick={handleEdit}>
        ✎
      </button>
    </div>
  );
};


// SAME REDUX UPDATE MECHANISM AS STATUS CELL
const CommitteeIdCell = connect(
  null,
  dispatch => ({
    updateInitiative: (initiativeId: string, values: any) =>
      dispatch(updateInitiativePipeline(initiativeId, values)),
  }),
)(CommitteeIdCellComponent);


[COMMITTEE_ID_COLUMN]: {
  Header: (
    <TableHeader label="INITIATIVE.PIPELINE.COMMITTEE_IDENTIFIER" />
  ),
  accessor: '_committeeIdentifier',

  Cell: (props: any) => (
    <CommitteeIdCell
      original={props.original}
      value={props.value}
    />
  ),

  minWidth: NumberGrid(20),
  className: 'center',
  Filter: () => null,
  sortable: false,
},