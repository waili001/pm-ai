/**
 * Converts Jira markup text to HTML.
 * Supports:
 * - Headers (h1-h6)
 * - Bold, Italic
 * - Unordered Lists
 * - Links
 * - Code blocks (simple)
 * - Text color (simple)
 */
export const jiraToHtml = (text) => {
    if (!text) return '';

    let html = text;

    // 1. Headers (h1. to h6.)
    // Note: Jira headers are h1. Text
    html = html.replace(/^h([1-6])\.\s+(.*)$/gm, '<h$1>$2</h$1>');

    // 2. Bold (*text*)
    html = html.replace(/\*([^\*]+)\*/g, '<strong>$1</strong>');

    // 3. Italic (_text_)
    html = html.replace(/_([^_]+)_/g, '<em>$1</em>');

    // 4. Monospace / Code ({{text}})
    html = html.replace(/\{\{([^}]+)\}\}/g, '<code>$1</code>');

    // 5. Code Blocks ({code} ... {code})
    html = html.replace(/\{code(?::([a-z]+))?\}([\s\S]*?)\{code\}/gm, '<pre><code>$2</code></pre>');

    // 6. Links ([Link Title|http://url] or [http://url])
    // Case 1: [Title|URL]
    html = html.replace(/\[([^|\]]+)\|([^\]]+)\]/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    // Case 2: [URL]
    html = html.replace(/\[([^\]]+)\]/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');

    // 7. Unordered Lists (* Item) - Simple support
    // Convert lines starting with * or - to list items
    // This is a naive implementation; proper nested lists require a parser state.
    // We'll wrap lines starting with * or - in <li>, then wrap groups in <ul> later or just styled div

    // Better approach for simple display:
    html = html.replace(/^[\*\-]\s+(.*)$/gm, '<li>$1</li>');

    // Wrap consecutive <li> in <ul> (Naive regex approach)
    // Finding blocks of <li>...</li> and wrapping them
    // This part is tricky with regex alone. 
    // Let's just wrap the whole thing in a div and styling will handle spacing.
    // Or we leave <li> floating which is bad HTML but browsers tolerate it.
    // Let's try to wrap at least simplisticly.
    // Actually, let's keep it simple: Replace <li> with a styled div or bullet char
    // html = html.replace(/<li>(.*)<\/li>/g, '<div style="margin-left: 20px;">• $1</div>');

    // Let's try to do <ul> wrapping:
    // html = html.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>'); // This regex is dangerous for large text

    // Fallback: Just bullet points
    // html = html.replace(/^[\*\-]\s+(.*)$/gm, '&bull; $1<br/>');

    // 8. Color ({color:red}text{color})
    html = html.replace(/\{color:([^}]+)\}(.*?)\{color\}/g, '<span style="color:$1">$2</span>');

    // 9. Newlines to <br/> (if not already handled by block elements)
    // We should preserve newlines.
    html = html.replace(/\n/g, '<br/>');

    return html;
};
