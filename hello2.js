const handleSave = () => {
  const preCommitteeDates = original?.committeeDates || [];

  // committeeDates contains only the Pre-Committee dates.
  // The last one is therefore the date immediately before Committee Date:
  //
  // []             -> no Pre-Committee Date
  // [pre1]         -> pre1
  // [pre1, pre2]   -> pre2

  const lastPreCommitteeDate =
    preCommitteeDates.length > 0
      ? preCommitteeDates[preCommitteeDates.length - 1]
      : null;

  // Same constraint as InitiativeDescription:
  // Committee Date must be STRICTLY after the last Pre-Committee Date.
  if (
    lastPreCommitteeDate &&
    new Date(editedValue) <= new Date(lastPreCommitteeDate)
  ) {
    setIsInvalidDateModalOpen(true);
    return;
  }

  updateInitiative(original.id, {
    committeeDate: editedValue,
    id: original.id,
    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};


<div>
  Committee Date must be after the last Pre-Committee Date.
</div>
