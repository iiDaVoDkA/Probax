export default {
  IconContainer: styled.div`
    margin-left: ${Grid(1.3)};
  `,

  Container: styled.div`
    background-color: white;
    padding: ${Grid(5)};
    width: 100%;
  `,

  // ... les autres styles

  ExpanderContainer: styled.span`
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
  `,

  ExpanderIcon: styled.span`
    display: inline-flex;
    transform: ${({ isOpen }) =>
      isOpen ? 'rotate(0deg)' : 'rotate(-90deg)'};
    transition: transform 0.5s ease;
  `,
};




return (
  <commonStyle.ExpanderContainer
    onClick={e => {
      e.stopPropagation();

      if (original.id != null) {
        toggleParent(original.id);
      }
    }}
  >
    <commonStyle.ExpanderIcon isOpen={original._isOpen}>
      <Icon slug="chevron-down" />
    </commonStyle.ExpanderIcon>
  </commonStyle.ExpanderContainer>
);
