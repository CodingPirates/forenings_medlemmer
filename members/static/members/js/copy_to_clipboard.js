document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.copy-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const url = button.getAttribute('data-url');
            navigator.clipboard.writeText(url).then(function() {
                alert('URL copied to clipboard!');
            }, function(err) {
                console.error('Could not copy text: ', err);
            });
        });
    });
});