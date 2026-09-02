Cell: ({ original }: { original: Object }) => {
  if (!original || !original._isParent || !original._hasChildren) {
    return null;
  }

  return (
    <span
      style={{ cursor: 'pointer', userSelect: 'none' }}
      onClick={e => {
        e.stopPropagation();

        if (original.id != null) {
          toggleParent(original.id);
        }
      }}
    >
      {original._isOpen ? (
        <Icon slug="chevron-down" />
      ) : (
        <Icon slug="chevron-right" />
      )}
    </span>
  );
}
