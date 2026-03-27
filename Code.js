// this function is called as soon as the document is opened
function onOpen() {
    // creates a menu under the menu bar
    // this has a button that lets the user open the sidebar
    DocumentApp.getUi()
        .createMenu("Wordless")
        .addItem("Open", "showSidebar")
        .addToUi();
    
    // every time the document is opened, the sidebar is too
    showSidebar();
}

function showSidebar() {
    // grabs the html from Index.html
    const html = HtmlService.createHtmlOutputFromFile("Index")
        .setTitle("Wordless"); // sets the title of the sidebar
    // this serves the html specifically as a sidebar
    // Google Apps Script also lets you do this as a dialog box instead
    DocumentApp.getUi()
        .showSidebar(html);
}

function applyStyle(rangeElements, style) {
    // loop over each range element
    rangeElements.forEach((rangeElement) => {
        // if the offset isn't found
        // skip this iteration
        // here in the forEach loop, return will act like continue
        if (rangeElement.getStartOffset() == -1 ||
            rangeElement.getEndOffsetInclusive() == -1)
            return;
        // set the style
        rangeElement.getElement()   // get the element
            .asText()               // convert to text
            .editAsText()           // make it editable
            .setAttributes(         // set the style
                rangeElement.getStartOffset(),
                rangeElement.getEndOffsetInclusive(),
                style
            )
    });
}

// this method is called to format selected text
// the formatType parameter determines what type of styling the text is given
function formatText(formatType) {
    try {
        // gets the text that the user is selecting
        // the output is a list of RangeElement objects
        // each range element encapsulates one paragraph
        var selection = DocumentApp.getActiveDocument().getSelection();
        if (selection)
            selection = selection.getRangeElements();

        // create an empty object for style attributes
        // this will be filled out and applied in the switch statement
        const style = {};

        // based on format type, configure the style for the text
        switch (formatType) {
            case "HIGHLIGHT":
                style[DocumentApp.Attribute.BACKGROUND_COLOR] = "#00ffff";
                applyStyle(selection, style);
                break;
            case "UNDERLINE":
                style[DocumentApp.Attribute.UNDERLINE] = true;
                applyStyle(selection, style);
                break;
            case "BOLD":
                style[DocumentApp.Attribute.BOLD] = true;
                applyStyle(selection, style);
                break;
            case "CONDENSE":
                for (let i = selection.length - 1; i > 0; i--) {
                    if (selection[i].getElement().asText().getText().trim() != "") {
                        selection[i].getElement().asText().editAsText().insertText(0, " ");
                    }
                    selection[i].getElement().merge();
                }
                break;
            case "FORMAT":
                var paragraphs = DocumentApp.getActiveDocument().getBody().getParagraphs();
                style[DocumentApp.Attribute.FONT_FAMILY] = "Palatino Linotype";
                style[DocumentApp.Attribute.FOREGROUND_COLOR] = "#000000";
                paragraphs.forEach((paragraph) => {
                    paragraph.setLineSpacing(1.15);
                    paragraph.setAttributes(style);
                });
                break;
            case "SHRINK":
                selection.forEach((rangeElement) => {
                    const textStart = rangeElement.getStartOffset();
                    const textEnd = rangeElement.getEndOffsetInclusive();
                    // if the offset isn't found
                    // skip this iteration
                    // here in the forEach loop, return will act like continue
                    if (rangeElement.getStartOffset() == -1 ||
                        rangeElement.getEndOffsetInclusive() == -1)
                        return;
                    for (let i = textStart; i < textEnd + 1; i++) {
                        const attributes = rangeElement.getElement().asText().getAttributes(i);
                        if (attributes.BOLD == null &&
                            attributes.UNDERLINE == null &&
                            attributes.BACKGROUND_COLOR == null) {
                                style[DocumentApp.Attribute.FONT_SIZE] = 8;
                                rangeElement.getElement()
                                    .asText()
                                    .editAsText()
                                    .setAttributes(i, i, style)
                        }
                    }
                });
                break;
            default:
                throw new Error("Unkown formatType passed to formatText()")
        }
    }
    catch(error) {
        console.error("Error message:", error.message);
        console.error("Stack trace:", error.stack);
    }
}
