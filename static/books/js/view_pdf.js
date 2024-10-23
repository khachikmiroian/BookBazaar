// Получаем URL PDF-файла из шаблона
var url = pdfUrl;

var pdfDoc = null,
    pageNum = 1,
    pageRendering = false,
    pageNumPending = null,
    scale = 1, // Начальный масштаб
    canvas = document.getElementById('pdf-viewer'),
    ctx = canvas.getContext('2d');

// Инициализация PDF.js worker
var pdfjsLib = window['pdfjs-dist/build/pdf'];
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.10.377/pdf.worker.min.js';

// Загрузка PDF документа
pdfjsLib.getDocument(url).promise.then(function(pdfDoc_) {
    pdfDoc = pdfDoc_;
    document.getElementById('page-count').textContent = pdfDoc.numPages;
    renderPage(pageNum);
});

// Функция рендеринга страницы
function renderPage(num) {
    pageRendering = true;
    pdfDoc.getPage(num).then(function(page) {
        var viewport = page.getViewport({ scale: scale });
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        var renderContext = {
            canvasContext: ctx,
            viewport: viewport
        };

        // Рендерим страницу
        page.render(renderContext).promise.then(function() {
            pageRendering = false;
            if (pageNumPending !== null) {
                renderPage(pageNumPending);
                pageNumPending = null;
            }
        });
    });
    document.getElementById('page-num').textContent = num;
}

function queueRenderPage(num) {
    if (pageRendering) {
        pageNumPending = num;
    } else {
        renderPage(num);
    }
}

// Навигация по страницам
document.getElementById('prev-page').addEventListener('click', function() {
    if (pageNum <= 1) {
        return;
    }
    pageNum--;
    queueRenderPage(pageNum);
});

document.getElementById('next-page').addEventListener('click', function() {
    if (pageNum >= pdfDoc.numPages) {
        return;
    }
    pageNum++;
    queueRenderPage(pageNum);
});

// Плавное увеличение/уменьшение масштаба
function smoothZoom(targetScale, cursorX, cursorY) {
    scale = targetScale;
    renderPage(pageNum); // Перерисовываем страницу с новым масштабом
}

// Увеличение и уменьшение масштаба
document.getElementById('zoom-in').addEventListener('click', function() {
    smoothZoom(scale + 0.1, canvas.width / 2, canvas.height / 2);
});

document.getElementById('zoom-out').addEventListener('click', function() {
    smoothZoom(scale - 0.1, canvas.width / 2, canvas.height / 2);
});

// Переход на конкретную страницу
document.getElementById('go-page').addEventListener('click', function() {
    var inputPage = parseInt(document.getElementById('page-input').value);
    if (inputPage > 0 && inputPage <= pdfDoc.numPages) {
        pageNum = inputPage;
        queueRenderPage(pageNum);
    }
});

// Переключение полноэкранного режима
function toggleFullscreen() {
    if (!document.fullscreenElement) {
        document.getElementById('pdf-container').requestFullscreen();
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Навигация с помощью клавиатуры
document.addEventListener('keydown', function(event) {
    switch (event.key) {
        case 'ArrowLeft':
            if (pageNum > 1) {
                pageNum--;
                queueRenderPage(pageNum);
            }
            break;
        case 'ArrowRight':
            if (pageNum < pdfDoc.numPages) {
                pageNum++;
                queueRenderPage(pageNum);
            }
            break;
        case 'f':
            toggleFullscreen();
            break;
        case 'Escape':
            if (document.fullscreenElement) {
                document.exitFullscreen();
            }
            break;
    }
});

// Прокрутка колесиком мыши с учетом положения курсора
var pdfContainer = document.getElementById('pdf-container');
pdfContainer.addEventListener('wheel', function(event) {
    event.preventDefault();
    var cursorX = event.clientX - canvas.getBoundingClientRect().left;
    var cursorY = event.clientY - canvas.getBoundingClientRect().top;
    if (event.deltaY < 0) {
        smoothZoom(scale + 0.1, cursorX, cursorY); // Увеличение
    } else {
        smoothZoom(scale - 0.1, cursorX, cursorY); // Уменьшение
    }
});

// Включение навигации по клавиатуре и зума в полноэкранном режиме
document.addEventListener('keydown', function(event) {
    if (document.fullscreenElement) {
        switch (event.key) {
            case 'ArrowLeft':
                if (pageNum > 1) {
                    pageNum--;
                    queueRenderPage(pageNum);
                }
                break;
            case 'ArrowRight':
                if (pageNum < pdfDoc.numPages) {
                    pageNum++;
                    queueRenderPage(pageNum);
                }
                break;
        }
    }
});
