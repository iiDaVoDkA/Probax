Cell: (props: any) => (
  <CommitteeDateCell
    key={`committee-date-${props.original.id}`}
    original={props.original}
    value={props.value}
  />
),