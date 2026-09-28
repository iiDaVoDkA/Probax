
formikBag.setStatus('Submit handler reached');

try {
  createTasks(values, initiative);
  formikBag.setStatus('Create action dispatched');
  closeInitiativeTaskForm();
} catch (error) {
  formikBag.setStatus(`Submit error: ${error.message}`);
}


status: this.props.status 
?? 'Submit handler not reached',

<pre style={{ color: 'red', whiteSpace: 'pre-wrap' }}>
  {JSON.stringify(
    {
      errors: this.props.errors,
      errorFields: Object.keys(this.props.errors || {}),
      submitCount: this.props.submitCount,
      isSubmitting: this.props.isSubmitting,
      isValidating: this.props.isValidating,
      status: this.props.status ?? 'Submit handler not reached',
    },
    null,
    2,
  )}
</pre>

