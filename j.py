<Style.ConfirmButton
  type="button"
  label={<FormattedMessage id={submitButtonLabel} />}
  mediumFont
  disabled={editedTask && editedTask.status === TASK_STATUS_DONE}
  onClick={async () => {
    this.props.setStatus('Starting Formik submission');

    try {
      await this.props.submitForm();
    } catch (error) {
      this.props.setStatus(
        `Formik error: ${error.message || String(error)}`,
      );
      this.props.setSubmitting(false);
    }
  }}
/>