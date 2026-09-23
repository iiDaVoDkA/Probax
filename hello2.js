const handleSave = () => {
  const preCommitteeDates = original?.committeeDates || [];

  const lastPreCommitteeDate =
    preCommitteeDates.length > 0
      ? preCommitteeDates[preCommitteeDates.length - 1]
      : null;

  // Same constraint as Initiative Description:
  // Committee Date must be strictly after the last Pre-Committee Date.
  if (
    lastPreCommitteeDate &&
    new Date(editedValue) <= new Date(lastPreCommitteeDate)
  ) {
    setIsInvalidDateModalOpen(true);
    return;
  }

  updateInitiative(original.id, {
    committeeDate: editedValue,
    committeeDates: preCommitteeDates,
    id: original.id,
    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};
