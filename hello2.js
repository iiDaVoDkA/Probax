

const committees = [
  ...(original.initiativeGovernance?.commitees || []),
].sort((a, b) => a.order - b.order);

const dates = committees.map(committee => {
  const entry = (original.initiativeCommiteeDates || []).find(
    item => String(item.commitee_id) === String(committee.id),
  );

  return entry ? entry.date : null;
});