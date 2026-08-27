REVIEW_TOOL = {
    "name": "submit_code_review",
    "description": "Submit a structured code review with an overall summary and a list of specific issues found.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "2-3 sentence overall assessment of the code.",
            },
            "overall_score": {
                "type": "integer",
                "minimum": 1,
                "maximum": 10,
                "description": "Overall code quality score, 1 (poor) to 10 (excellent).",
            },
            "issues": {
                "type": "array",
                "description": "Specific issues found, ordered by severity (most severe first). Empty if the code has no issues.",
                "items": {
                    "type": "object",
                    "properties": {
                        "severity": {
                            "type": "string",
                            "enum": ["critical", "warning", "suggestion"],
                            "description": "critical = bug/security issue that will cause incorrect behavior; warning = risky pattern or likely bug; suggestion = style/readability/best-practice improvement.",
                        },
                        "category": {
                            "type": "string",
                            "enum": ["bug", "security", "performance", "style", "best-practice", "test-coverage"],
                        },
                        "line": {
                            "type": "integer",
                            "description": "1-indexed line number this issue relates to, or 0 if it's not tied to a specific line.",
                        },
                        "title": {
                            "type": "string",
                            "description": "Short (< 60 char) label for the issue.",
                        },
                        "description": {
                            "type": "string",
                            "description": "What's wrong and why it matters, 1-3 sentences.",
                        },
                        "suggestion": {
                            "type": "string",
                            "description": "Concrete fix or improvement, may include a short code snippet.",
                        },
                    },
                    "required": ["severity", "category", "line", "title", "description", "suggestion"],
                },
            },
        },
        "required": ["summary", "overall_score", "issues"],
    },
}
