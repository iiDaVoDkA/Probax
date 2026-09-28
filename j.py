
formikBag.setStatus('Submit handler reached');

try {
  createTasks(values, initiative);
  formikBag.setStatus('Create action dispatched');
  closeInitiativeTaskForm();
} catch (error) {
  formikBag.setStatus(`Submit error: ${error.message}`);
}


status: this.props.status ?? 'Submit handler not reached',