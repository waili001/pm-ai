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
            const content = parseInline(headingMatch[2]);
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
            const content = parseInline(ulMatch[2]);
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
            const content = parseInline(olMatch[2]);
            elements.push({
                type: 'oli',
                content,
                depth,
                key: `oli-${index}`
            });
            return;
        }

        // Regular paragraph with bold and link parsing
        const content = parseInline(line);
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

/**
 * Parse text for links first, then bold
 * Supports [url] and [text|url]
 */
function parseInline(text) {
    // Regex for links: [label|url] or [url]
    // We strictly look for http/https in the url part
    const linkRegex = /\[(?:([^|\]]+)\|)?(https?:\/\/[^\]]+)\]/g;

    const parts = [];
    let lastIndex = 0;
    let match;

    while ((match = linkRegex.exec(text)) !== null) {
        // Add text before the link
        if (match.index > lastIndex) {
            const textPart = text.substring(lastIndex, match.index);
            parts.push(...parseBold(textPart));
        }

        const label = match[1];
        const href = match[2];
        const displayText = label || href;

        parts.push({
            link: true,
            text: displayText,
            href: href
        });

        lastIndex = linkRegex.lastIndex;
    }

    // Add remaining text
    if (lastIndex < text.length) {
        parts.push(...parseBold(text.substring(lastIndex)));
    }

    return parts.length > 0 ? parts : [text];
}
