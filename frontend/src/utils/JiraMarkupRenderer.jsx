import { Box, Typography, Link } from '@mui/material';
import { parseJiraMarkup } from './jiraMarkup';

/**
 * Component to render Jira Wiki Markup as React elements
 */
export function JiraMarkupRenderer({ text }) {
    if (!text) return <Typography variant="body2">No description provided.</Typography>;

    const elements = parseJiraMarkup(text);

    return (
        <Box>
            {elements.map((el, idx) => {
                // Render text parts (handle bold and links)
                const renderText = (content) => {
                    if (typeof content === 'string') return content;
                    if (Array.isArray(content)) {
                        return content.map((part, i) => {
                            if (typeof part === 'string') return <span key={i}>{part}</span>;
                            if (part.bold) return <strong key={i}>{part.text}</strong>;
                            if (part.link) {
                                return (
                                    <Link key={i} href={part.href} target="_blank" rel="noopener noreferrer" underline="hover">
                                        {part.text}
                                    </Link>
                                );
                            }
                            return part;
                        });
                    }
                    return content;
                };

                // Headings
                if (el.type === 'h1') return <Typography variant="h4" key={el.key} gutterBottom sx={{ mt: 2, fontWeight: 'bold' }}>{renderText(el.content)}</Typography>;
                if (el.type === 'h2') return <Typography variant="h5" key={el.key} gutterBottom sx={{ mt: 2, fontWeight: 'bold' }}>{renderText(el.content)}</Typography>;
                if (el.type === 'h3') return <Typography variant="h6" key={el.key} gutterBottom sx={{ mt: 1.5, fontWeight: 'bold' }}>{renderText(el.content)}</Typography>;
                if (el.type === 'h4') return <Typography variant="subtitle1" key={el.key} gutterBottom sx={{ mt: 1.5, fontWeight: 'bold' }}>{renderText(el.content)}</Typography>;
                if (el.type === 'h5') return <Typography variant="subtitle2" key={el.key} gutterBottom sx={{ mt: 1, fontWeight: 'bold' }}>{renderText(el.content)}</Typography>;
                if (el.type === 'h6') return <Typography variant="caption" key={el.key} gutterBottom sx={{ mt: 1, fontWeight: 'bold', display: 'block' }}>{renderText(el.content)}</Typography>;

                // Line break
                if (el.type === 'br') return <Box key={el.key} sx={{ height: 8 }} />;

                // List items (unordered and ordered)
                if (el.type === 'li' || el.type === 'oli') {
                    const indent = (el.depth - 1) * 24;
                    return (
                        <Box key={el.key} sx={{ pl: `${indent}px`, display: 'flex', gap: 1 }}>
                            <Typography variant="body2" component="span">
                                {el.type === 'li' ? '•' : `${idx + 1}.`}
                            </Typography>
                            <Typography variant="body2" component="span">
                                {renderText(el.content)}
                            </Typography>
                        </Box>
                    );
                }

                // Paragraph
                if (el.type === 'p') {
                    return <Typography variant="body2" key={el.key} paragraph>{renderText(el.content)}</Typography>;
                }

                return null;
            })}
        </Box>
    );
}
