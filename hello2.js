Yes. Keep your existing findIndex() approach and add the validation around it. In CommitteeDateCellComponent, make these exact changes.

1. Add this state next to your existing isEditing / editedValue

const [isInvalidDateModalOpen, setIsInvalidDateModalOpen] =
  React.useState(false);

So the beginning becomes:

const CommitteeDateCellComponent = ({
  original,
  value,
  updateInitiative,
  getInitiativePipeline,
}: any) => {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editedValue, setEditedValue] = React.useState(value || '');
  // ADD THIS
  const [isInvalidDateModalOpen, setIsInvalidDateModalOpen] =
    React.useState(false);

2. Replace your current handleSave completely with this

const handleSave = () => {
  const committeeDates = original?.committeeDates || [];
  // Keep your existing findIndex logic
  const indexToReplace = committeeDates.findIndex(
    date => date === original?.committeeDate,
  );
  // If Committee Date was found and has a value before it,
  // that previous value is the Pre-Committee Date
  const preCommitteeDate =
    indexToReplace > 0
      ? committeeDates[indexToReplace - 1]
      : null;
  // Committee Date must NOT be before Pre-Committee Date
  if (
    preCommitteeDate &&
    new Date(editedValue) < new Date(preCommitteeDate)
  ) {
    setIsInvalidDateModalOpen(true);
    return;
  }
  // Keep your replacement logic.
  // If there was no previous Committee Date, create it.
  const updatedDates =
    indexToReplace === -1
      ? [...committeeDates, editedValue]
      : committeeDates.map((date, i) =>
          i === indexToReplace ? editedValue : date
        );
  updateInitiative(original.id, {
    committeeDate: editedValue,
    committeeDates: updatedDates,
    id: original.id,
    updatedFromGlobalScreen: true,
  });
  setIsEditing(false);
};

This handles all your cases:

[] 
→ no Pre-Committee Date
→ save new Committee Date
[Committee Date]
→ index = 0
→ no Pre-Committee Date
→ modify normally
[Pre-Committee Date, Committee Date]
→ index = 1
→ previous value = Pre-Committee Date
→ compare before saving

3. Add this modal inside CommitteeDateCellComponent

Important: because your component currently does:

if (isEditing) {
  return (...);
}
return (...);

you need the modal available in the editing return, because that’s when Save can fail.

Inside:

if (isEditing) {
  return (

wrap your existing content in a fragment <>...</> and add the modal after your editing <div>:

if (isEditing) {
  return (
    <>
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
        {/* KEEP YOUR EXISTING SAVE / CANCEL BUTTONS HERE */}
      </div>
      {/* ADD THIS */}
      <Modal
        isOpen={isInvalidDateModalOpen}
        onCloseClick={() => setIsInvalidDateModalOpen(false)}
        width={Grid(6)}
      >
        <div
          style={{
            padding: 30,
            textAlign: 'center',
          }}
        >
          <div>
            Committee Date cannot be earlier than Pre-Committee Date.
          </div>
          <div
            style={{
              marginTop: 30,
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <Button
              type="button"
              label="OK"
              onClick={() => setIsInvalidDateModalOpen(false)}
            />
          </div>
        </div>
      </Modal>
    </>
  );
}

So your final behavior is:

Pre-Committee = 20/09
Committee     = 25/09
User enters 18/09
        ↓
comparison fails
        ↓
error popup
        ↓
NO updateInitiative() ✅
input remains open ✅
User enters 22/09
        ↓
valid
        ↓
updateInitiative() ✅

One detail: if your API dates are ISO values such as 2026-09-20 / 2026-09-20T00:00:00, new Date(...) is fine. If committeeDates contains strings formatted like 20/09/2026, tell me, because then we should use the moment already present in your project rather than new Date().