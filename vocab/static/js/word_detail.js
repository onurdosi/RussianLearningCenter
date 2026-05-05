document.addEventListener("DOMContentLoaded", function () {
    const wordButtons = document.querySelectorAll('.word-tile');
    const detailPanel = document.getElementById('word-detail-panel');
    const detailRussianWord = document.getElementById('detail-russian-word');
    const detailTranslation = document.getElementById('detail-translation');
    const detailDifficulty = document.getElementById('detail-difficulty');
    const detailNotes = document.getElementById('detail-notes');
    const detailNotesRow = document.getElementById('detail-notes-row');
    const detailEditLink = document.getElementById('detail-edit-link');
    const detailDeleteLink = document.getElementById('detail-delete-link');

    let selectedWord = null;

    wordButtons.forEach((button) => {
        button.addEventListener('click', () => {
            if (selectedWord === button) {
                detailPanel.classList.add('hidden');
                button.classList.remove('selected-word');
                selectedWord = null;
                return;
            }

            wordButtons.forEach((wordButton) => {
                wordButton.classList.remove('selected-word');
            });

            selectedWord = button;
            button.classList.add('selected-word');

            detailRussianWord.textContent = button.dataset.russian;
            detailTranslation.textContent = button.dataset.translation;
            detailDifficulty.textContent = button.dataset.difficulty;
            detailEditLink.href = button.dataset.editUrl;
            detailDeleteLink.href = button.dataset.deleteUrl;

            if (button.dataset.notes) {
                detailNotes.textContent = button.dataset.notes;
                detailNotesRow.style.display = 'block';
            } else {
                detailNotes.textContent = '';
                detailNotesRow.style.display = 'none';
            }

            detailPanel.classList.remove('hidden');
        });
    });
});