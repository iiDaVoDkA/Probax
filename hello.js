<span
  style={{
    width: '100%',
    height: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    userSelect: 'none',
  }}
  onClick={e => {
    e.stopPropagation();

    if (original.id != null) {
      toggleParent(original.id);
    }
  }}
>
  <span
    style={{
      display: 'inline-flex',
      transform: original._isOpen
        ? 'rotate(0deg)'
        : 'rotate(-90deg)',
    }}
  >
    <Icon slug="chevron-down" />
  </span>
</span>
