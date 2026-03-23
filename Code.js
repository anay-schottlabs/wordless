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

function getSelectionText(rangeElement) {
    const start = rangeElement.getStartOffset();
    const end = rangeElement.getEndOffsetInclusive();
    return rangeElement.getElement()    // get the element
        .asText()                       // convert to text
        .getText()                      // extract all text (not just selection)
        .slice(start, end + 1);         // use text positions to cut out only selection
}

// this method is called to format selected text
// the formatType parameter determines what type of styling the text is given
function formatText(formatType) {
    try {
        // gets the text that the user is selecting
        // the output is a list of RangeElement objects
        // each range element encapsulates one type of style
        // if something is bolded, underlined, or has any other attribute, it gets its own range element
        // each selection can go over multiple styles, so each one has plenty of range elements
        // each new paragraph also creates another range element
        const selection = DocumentApp.getActiveDocument().getSelection().getRangeElements();

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
                // let text = "";
                // selection.forEach((rangeElement) => {
                //     text = text.concat(" ", getSelectionText(rangeElement));
                // });

                // const body = DocumentApp.getActiveDocument().getBody().editAsText();
                // break;
            case "SHRINK":
                console.log(selection[0].getElement().getAttributes());
                selection.forEach((rangeElement) => {
                    if (rangeElement.getElement().getAttributes().length == 0) {
                        style[DocumentApp.Attribute.FONT_SIZE] = 8;
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
