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

function applyStyle(textStart, textEnd, style) {
    // apply the style attributes to the text
    DocumentApp.getActiveDocument()
        .getBody()
        .editAsText()
        .setAttributes(textStart, textEnd, style);
}

// this method is called to format selected text
// the formatType parameter determines what type of styling the text is given
function formatText(formatType) {
    try {
        // gets the text that the user is selecting
        const selection = DocumentApp.getActiveDocument().getSelection().getRangeElements();
        const textStart = selection[0].getStartOffset();
        const textEnd = selection[0].getEndOffsetInclusive();

        // create an empty object for style attributes
        // this will be filled out and applied in the switch statement
        const style = {};

        // based on format type, configure the style for the text
        switch (formatType) {
            case "HIGHLIGHT":
                style[DocumentApp.Attribute.BACKGROUND_COLOR] = "#00ffff";
                applyStyle(textStart, textEnd, style);
                break;
            case "UNDERLINE":
                style[DocumentApp.Attribute.UNDERLINE] = true;
                applyStyle(textStart, textEnd, style);
                break;
            case "BOLD":
                style[DocumentApp.Attribute.BOLD] = true;
                applyStyle(textStart, textEnd, style);
                break;
            case "CONDENSE":
                const body = DocumentApp.getActiveDocument().getBody();
                console.log(`Before: ${body.getText().slice(textStart, textEnd + 1)}`)
                const text = body.getText().slice(textStart, textEnd + 1).replaceAll("\n", "");
                console.log(`After: ${text}`);
                break;
            case "SHRINK":
                break;
            default:
                throw new Error("Unkown formatType passed to formatText()")
        }
    }
    catch(error) {
        console.log(error);
    }
}
