document.addEventListener('DOMContentLoaded', function() {
    const departmentSelect = document.getElementById('id_department');
    const activitySelect = document.getElementById('id_activity');
    if (departmentSelect) {
        departmentSelect.addEventListener('change', function() {
            const departmentId = this.value;
            if (!departmentId) {
                activitySelect.innerHTML = '<option value="">---------</option>';
                return;
            }

            fetch(`/admin_members_activity_by_department/${departmentId}/`)
                .then(response => response.json())
                .then(data => {
                    let options = '<option value="">---------</option>';
                    data.activities.forEach(activity => {
                        options += `<option value="${activity.id}">${activity.name}</option>`;
                    });
                    activitySelect.innerHTML = options;
                    
                    // Preserve the selected value if it exists
                    const selectedValue = activitySelect.getAttribute('data-selected-value');
                    if (selectedValue) {
                        activitySelect.value = selectedValue;
                    }
                });
                   
        });

        // Trigger change event on page load to populate activities if a department is already selected

        if (departmentSelect.value) {
            const event = new Event('change');
            departmentSelect.dispatchEvent(event);
        }        
    }
});