var url = "{{ book.pdf_file.url }}";
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
function smoothZoom(targetScale) {
    scale = targetScale;
    renderPage(pageNum); // Перерисовываем страницу с новым масштабом
}

// Увеличение и уменьшение масштаба
document.getElementById('zoom-in').addEventListener('click', function() {
    smoothZoom(scale + 0.1);
});

document.getElementById('zoom-out').addEventListener('click', function() {
    smoothZoom(scale - 0.1);
});

// Переход на конкретную страницу
document.getElementById('go-page').addEventListener('click', function() {
    var inputPage = parseInt(document.getElementById('page-input').value);
    if (inputPage > 0 && inputPage <= pdfDoc.numPages) {
        pageNum = inputPage;
        queueRenderPage(pageNum);
