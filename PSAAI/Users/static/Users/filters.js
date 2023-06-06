function filterExam(btn) {
    var filters = document.getElementById('filters');
    var buttonValue = btn.innerHTML; // Get the inner text of the clicked button
  
    if (filters.value === '') {
      filters.value = buttonValue;
    } else {
      filters.value += ' ' + buttonValue;
    }
  }