/**
 * Parse Jira Wiki Markup and convert to React elements
 * Supports: headings (h1-h6), bold (*), lists (*, #), line breaks
 */

export function parseJiraMarkup(text) {
    if (!text) return [];

    const lines = text.split(/\r?\n/);
    const elements = [];
    let listStack = []; // Track nested lists

    lines.forEach((line, index) => {
        // Skip empty lines in output but keep for formatting
        if (line.trim() === '') {
            elements.push({ type: 'br', key: `br-${index}` });
            return;
        }

        // Headings: h1. h2. h3. etc.
        const headingMatch = line.match(/^h([1-6])\.\s*(.+)$/);
        if (headingMatch) {
            const level = parseInt(headingMatch[1]);
            const content = parseBold(headingMatch[2]);
            elements.push({
                type: `h${level}`,
                content,
                key: `h${level}-${index}`
            });
            return;
        }

        // Unordered List: * item or ** sub-item
        const ulMatch = line.match(/^(\*+)\s+(.+)$/);
        if (ulMatch) {
            const depth = ulMatch[1].length;
            const content = parseBold(ulMatch[2]);
            elements.push({
                type: 'li',
                content,
                depth,
                key: `li-${index}`
            });
            return;
        }

        // Ordered List: # item or ## sub-item
        const olMatch = line.match(/^(#+)\s+(.+)$/);
        if (olMatch) {
            const depth = olMatch[1].length;
            const content = parseBold(olMatch[2]);
            elements.push({
                type: 'oli',
                content,
                depth,
                key: `oli-${index}`
            });
            return;
        }

        // Regular paragraph with bold parsing
        const content = parseBold(line);
        elements.push({
            type: 'p',
            content,
            key: `p-${index}`
        });
    });

    return elements;
}

/**
 * Parse bold text: *bold* -> <strong>
 * Returns array of strings and {bold: true, text: "..."} objects
 */
function parseBold(text) {
    const parts = [];
    let current = '';
    let inBold = false;
    let i = 0;

    while (i < text.length) {
        if (text[i] === '*') {
            // Check if it's escaped or part of list marker
            if (i > 0 && text[i - 1] === '\\') {
                current += '*';
                i++;
                continue;
            }

            // Toggle bold
            if (current) {
                parts.push(inBold ? { bold: true, text: current } : current);
                current = '';
            }
            inBold = !inBold;
            i++;
        } else {
            current += text[i];
            i++;
        }
    }

    if (current) {
        parts.push(inBold ? { bold: true, text: current } : current);
    }

    return parts.length > 0 ? parts : [text];
}
