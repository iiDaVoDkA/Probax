updateInitiative(original.id, {
  ...original,
  committeeDate: editedValue,
  committeeDates: original?.committeeDates?.map((date, index, dates) =>
    index === dates.length - 1 ? editedValue : date
  ),
  id: original.id,
  updatedFromGlobalScreen: true,
});
