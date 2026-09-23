const handleSave = () => {
  const nbCommittees =
    original?.initiativeGovernance?.committees?.length;

  const selectedDate = new Date(editedValue);

  if (nbCommittees === 2) {
    const pre1 = original?.committeeDates?.[0];

    if (pre1 && selectedDate <= new Date(pre1)) {
      setIsInvalidDateModalOpen(true);
      return;
    }
  }

  if (nbCommittees === 3) {
    const pre2 = original?.committeeDates?.[1];

    if (pre2 && selectedDate <= new Date(pre2)) {
      setIsInvalidDateModalOpen(true);
      return;
    }
  }

  updateInitiative(original.id, {
    committeeDate: editedValue,
    id: original.id,
    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};
