The screenshots show two null-safety bugs matching the crash: mainAssessor.value and the unguarded risks.value reads.

1. Replace the read-only MAIN ASSESSOR <select>, around lines 1055–1064, with:

<select
  value={ratingEditValues.mainAssessor?.value ?? ''}
  style={fullWidthInput}
  disabled={true}
>
  <option value="" />
  {ratingEditValues.mainAssessor && (
    <option value={ratingEditValues.mainAssessor.value}>
      {ratingEditValues.mainAssessor.label}
    </option>
  )}
</select>

A task assigned only to a team can have no individual assessor. This displays an empty selection safely. Keep the surrounding permission condition.

2. Fix the four unguarded rating accesses in the Done and Validate modals, around lines 1253, 1258, 1295 and 1300.

Replace:

ratingEditValues.risks.value

with:

ratingEditValues.risks?.value

For example, each modal’s height becomes:

height={
  ratingEditValues.comment && ratingEditValues.risks?.value
    ? Grid(40)
    : Grid(33)
}

And its confirmation condition becomes:

(ratingEditValues.comment && ratingEditValues.risks?.value) ||
(ratingEditValues.comment && ratingEditValues.type === 'OTHER')

These expressions are evaluated during the parent’s render even when the modal is closed, which explains how they can crash the whole tasks tab.

This preserves the visible validation rule: assessment tasks require a comment and rating; OTHER tasks require a comment. The rating dropdown around line 1131 already checks for null.

After applying these changes, reload and check:

* A task without a main assessor opens successfully.
* An individually assigned task still displays its assessor.
* An assessment with a comment but no rating cannot be completed.

I can identify these unsafe accesses from the screenshots; confirming which one triggered your particular render requires running the updated page.