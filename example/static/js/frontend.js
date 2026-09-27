// Apply font based on selected glyph set and display font name
export function updateVariantFont() {
    // Get selected glyph set and determine corresponding font
    const glyphSet = document.getElementById("glyph_set").value;

    let font = "inherit";
    let fontName = "";

    if (glyphSet === "mj-plus") {
        font = "DWPIMincho";
        fontName = "DWPIMincho";
    } else if (glyphSet === "mj-plusx") {
        font = "DWPIexMincho";
        fontName = "DWPIexMincho";
    } else if (glyphSet === "mj" || glyphSet === "mj-onka") {
        font = "IPAmjMincho";
        fontName = "IPAmjMincho";
    }

    // Apply font
    const jsonArea = document.getElementById("json_result");
    jsonArea.style.fontFamily = font;
    const variantInput = document.getElementById("variant_text");
    variantInput.style.fontFamily = font;

    // Display selected font name
    const fontNameLabel = document.getElementById("font_name");
    fontNameLabel.textContent = fontName;
}

// Call convert API and update UI
export async function doConvert() {
    const glyphSet = document.getElementById("glyph_set").value;
    const text = document.getElementById("text").value;

    const encodedText = encodeURIComponent(text);
    const url = `/convert/${glyphSet}/${encodedText}`;

    try {
        const res = await fetch(url);
        const data = await res.json();

        document.getElementById("json_result").value =
            JSON.stringify(data, null, 2);

        // Update normalized text
        const normalizedInput = document.getElementById("normalized_text");
        normalizedInput.value = data.text?.normalized || "";
        // Trigger input event to execute onNormalizedTextChange() in HTML
        normalizedInput.dispatchEvent(new Event("input"));

        updateVariantFont();

    } catch (err) {
        alert("Error calling /convert: " + err);
    }
}

// Initialize font on page load
export function initConsole() {
    updateVariantFont();
}
