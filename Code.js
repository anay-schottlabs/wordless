function onOpen() {
    DocumentApp.getUi()
        .createMenu("Wordless")
        .addItem("Open", "showSidebar")
        .addToUi();
    showSidebar();
}

function showSidebar() {
    const html = HtmlService.createHtmlOutputFromFile("Index")
        .setTitle("Wordless");
    DocumentApp.getUi()
        .showSidebar(html);
}

function formatText(formatType) {
    try{
    // const body = DocumentApp.getActiveDocument().getBody();
    const selection = DocumentApp.getActiveDocument().getSelection().getRangeElements()[0];
    console.log(selection);
    console.log(selection.getStartOffset());
    body.insertParagraph(selection.getStartOffset(), "text");
    DocumentApp.getActiveDocument().saveAndClose();
    }
    catch(error){
        console.log(error);
    }
}
