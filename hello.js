<SubSection
  title={
    <FormattedMessage
      id="INITIATIVE_DATA.SUBSECTION.BUSINESS"
      defaultMessage="Business"
    />
  }
>
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      gap: 16,
    }}
  >
    <SmartField
      isEditing={isEditing}
      intl={intl}
      name="aumExpected"
      labelId="INITIATIVE_DATA.AUM_EXPECTED"
      component={CommonStyle.Input}
      data={initiative}
      displaySnakeKey="aum_expected"
    />

    <SmartField
      isEditing={isEditing}
      intl={intl}
      name="commentsBusiness"
      labelId="INITIATIVE_DATA.COMMENTS_BUSINESS"
      component={TextArea}
      fieldProps={LongTextProps}
      data={initiative}
      displaySnakeKey="commentsBusiness"
    />
  </div>

  <SmartField
    isEditing={isEditing}
    intl={intl}
    name="feesDesc"
    labelId="INITIATIVE_DATA.FEES_DESC"
    component={TextArea}
    fieldProps={LongTextProps}
    data={initiative}
    displaySnakeKey="fees_desc"
  />
</SubSection>
