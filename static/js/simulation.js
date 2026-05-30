document.querySelectorAll('.sim-answer').forEach(btn => {
    btn.addEventListener('click', async function () {
        const card = document.getElementById('simCard');
        const type = card.dataset.type;
        const index = parseInt(card.dataset.index, 10);
        const answer = this.dataset.answer;
        const res = await fetch('/simulation/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type, index, answer })
        });
        const data = await res.json();
        const box = document.getElementById('simFeedback');
        const cls = data.correct ? 'alert-success' : 'alert-danger';
        box.innerHTML = `<div class="alert ${cls}">
            ${data.correct ? 'Correct!' : 'Incorrect. Correct answer: ' + data.correct_answer}
            <hr><p class="mb-0">${data.feedback}</p>
        </div>`;
    });
});
