const handleSave = () => {
  const indexToReplace = original.committeeDates.findIndex(
    date => date === original.committeeDate,
  );

  if (indexToReplace === -1) {
    return;
  }

  const selectedDate = new Date(editedValue);

  const previousDate =
    indexToReplace > 0
      ? original.committeeDates[indexToReplace - 1]
      : null;

  const nextDate =
    indexToReplace < original.committeeDates.length - 1
      ? original.committeeDates[indexToReplace + 1]
      : null;

  if (previousDate && selectedDate <= new Date(previousDate)) {
    return;
  }

  if (nextDate && selectedDate >= new Date(nextDate)) {
    return;
  }

  const updatedDates = original.committeeDates.map((date, i) =>
    i === indexToReplace ? editedValue : date,
  );

  updateInitiative(original.id, {
    committeeDate: editedValue,
    committeeDates: updatedDates,
    id: original.id,
    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};
