[INITIATIVE_EDIT_COLUMN]: {
  Header: <TableHeader label="INITIATIVE_EDIT" sortable={false} />,
  id: 'initiativeEdit',
  minWidth: NumberGrid(12),
  className: 'center',

  Cell: ({ original }: any) => {
    const canEdit =
      isAdmin ||
      original.initiativeOwnerId === user.id;

    if (!canEdit) {
      return null;
    }

    return (
      <IconButton
        hoverColor={BNPColors.ceruleanBlue}
        onClick={() => onEditInitiative(original)}
      >
        <Icon slug="pen" size={16} />
      </IconButton>
    );
  },

  sortable: false,
  filterable: false,
},