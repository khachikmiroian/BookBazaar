function toggleEditOptions(commentId) {
    const options = document.getElementById(`edit-options-${commentId}`);
    options.style.display = options.style.display === 'none' ? 'block' : 'none';
}

function editComment(commentId, content) {
    const commentElement = document.getElementById(`comment-${commentId}`);
    const commentContentElement = commentElement.querySelector('.comment-content');

    // Устанавливаем текстовое поле в текущее содержание комментария
    document.getElementById('comment-input').value = content;

    // Показать форму редактирования
    toggleEditOptions(commentId);

    // Создаем форму редактирования комментария
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = "{% url 'books:update_comment' 0 %}".replace('0', commentId); // Заменяем commentId на реальный ID

    // Добавляем csrf_token
    const csrfToken = '{{ csrf_token }}';
    form.innerHTML = `
        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
        <textarea name="content" style="width: 100%;">${content}</textarea>
        <button type="submit" class="btn btn-primary">Сохранить</button>
        <button type="button" class="btn btn-secondary" onclick="toggleEditOptions(${commentId})">Отменить</button>
    `;

    // Заменяем существующий контент комментария на форму
    commentContentElement.parentElement.replaceChild(form, commentContentElement);
}

function loadMoreComments() {
    const commentsContainer = document.getElementById('comments-container');
    // Имитация загрузки дополнительных комментариев
    // Добавьте ваш AJAX-запрос для получения и добавления комментариев
}
