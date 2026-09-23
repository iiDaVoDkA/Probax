const [dateError, setDateError] = React.useState('');

const handleSave = () => {
  setDateError('');

  const selectedDate = new Date(editedValue);

  if (!editedValue || Number.isNaN(selectedDate.getTime())) {
    setDateError('Please select a valid date.');
    return;
  }

  const committees = [
    ...(original.initiativeGovernance?.committees || []),
  ].sort((a, b) => a.order - b.order);

  const committeeIndex = committees.findIndex(
    committee => committee.id === original.__committeeId,
  );

  if (committeeIndex === -1) {
    setDateError('Unable to identify the committee for this row.');
    return;
  }

  const dates = committees.map(committee => {
    const entry = (original.initiativeCommitteeDates || []).find(
      item => item.committee_id === committee.id,
    );

    return entry ? entry.date : null;
  });

  const previousDate = dates[committeeIndex - 1];
  const nextDate = dates[committeeIndex + 1];

  if (previousDate && selectedDate <= new Date(previousDate)) {
    setDateError(`This date has to be after ${previousDate}.`);
    return;
  }

  if (nextDate && selectedDate >= new Date(nextDate)) {
    setDateError(`This date has to be before ${nextDate}.`);
    return;
  }

  const updatedDates = dates.map((date, index) =>
    index === committeeIndex ? editedValue : date,
  );

  updateInitiative(original.id, {
    committeeDate: updatedDates[updatedDates.length - 1],
    committeeDates: updatedDates,
    id: original.id,
    updatedFromGlobalScreen: true,
  });

  setIsEditing(false);
};


{dateError && (
  <span role="alert" style={{ color: 'red', whiteSpace: 'normal' }}>
    {dateError}
  </span>
)}