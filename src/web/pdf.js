function filenameFromUrl(url) {
    const components = url.split("/");
    const filename = components[components.length - 1];
    return decodeURIComponent(filename);
}

function onPDFViewerLoaded() {
    const pdfWindow = window.frames[0];
    const PDFViewerApplication = pdfWindow.PDFViewerApplication;
    PDFViewerApplication.initializedPromise.then(function () {
        PDFViewerApplication.eventBus.on('pagechanging', function pagechange(event) {
            const filename = filenameFromUrl(PDFViewerApplication.url);
            pycmd(`media-progress-tracker:set:${filename}:${event.pageNumber}`);
        });
    });
}

function renderPDFLinks(basePath) {
    const links = document.getElementById("qa").querySelectorAll('a[href$=".pdf"]');
    links.forEach(link => {
        const filename = filenameFromUrl(link.href);
        pycmd(`media-progress-tracker:get:${filename}`, fileData => {
            const page = fileData.page;
            const container = document.createElement("div");
            container.classList.add("resizer", "ugly");
            const iframe = document.createElement("iframe");
            iframe.classList.add("resized");
            iframe.width = 800;
            iframe.height = 600;
            iframe.src = `${basePath}/vendor/pdfjs/web/viewer.html?file=${link.href}#page=${page}`;
            iframe.onload = onPDFViewerLoaded;
            container.appendChild(iframe);
            link.replaceWith(container);
        })
    });
}
