// Interactive feedback for SettleSense UI

document.addEventListener('DOMContentLoaded', function() {
    // Toggle button highlight
    const oweBtn = document.getElementById('oweBtn');
    const theyOweBtn = document.getElementById('theyOweBtn');
    oweBtn.addEventListener('click', function() {
        oweBtn.classList.add('active');
        theyOweBtn.classList.remove('active');
    });
    theyOweBtn.addEventListener('click', function() {
        theyOweBtn.classList.add('active');
        oweBtn.classList.remove('active');
    });

    // Add button feedback
    const addBtn = document.getElementById('addBtn');
    const form = document.querySelector('.entry-form');
    addBtn.addEventListener('mousedown', function() {
        addBtn.classList.add('pressed');
    });
    addBtn.addEventListener('mouseup', function() {
        addBtn.classList.remove('pressed');
    });
    addBtn.addEventListener('mouseleave', function() {
        addBtn.classList.remove('pressed');
    });

    // Form submit feedback
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        addBtn.textContent = 'Added!';
        addBtn.style.background = '#4cd964';
        setTimeout(() => {
            addBtn.textContent = 'Add';
            addBtn.style.background = '';
        }, 1200);
        form.reset();
        oweBtn.classList.add('active');
        theyOweBtn.classList.remove('active');
    });
});
