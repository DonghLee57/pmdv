# coding: utf-8
import urllib.request
import gzip
import base64
import os
import sys

TIMEOUT = 15

ASSET_URLS = {
    "github_css": "https://cdn.jsdelivr.net/npm/github-markdown-css@5.5.1/github-markdown.min.css",
    "prism_css": "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/themes/prism-tomorrow.min.css",
    "katex_css": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
    "marked_js": "https://cdn.jsdelivr.net/npm/marked@12.0.1/marked.min.js",
    "markdown_it_js": "https://cdn.jsdelivr.net/npm/markdown-it@14.1.0/dist/markdown-it.min.js",
    "prism_js": "https://cdn.jsdelivr.net/npm/prismjs@1.29.0/prism.min.js",
    "katex_js": "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",
    "mermaid_js": "https://cdn.jsdelivr.net/npm/mermaid@9.4.3/dist/mermaid.min.js"
}

VIEWER_TEMPLATE = r"""import os
import sys
import time
import threading
import json
import gzip
import base64
import webview
# coding: utf-8
# PMDV Standalone Offline Markdown Viewer
# units: s, ms


ASSETS = {
    "github_css": b__TRIPLE_QUOTE_PLACEHOLDER__$GITHUB_CSS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "prism_css": b__TRIPLE_QUOTE_PLACEHOLDER__$PRISM_CSS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "katex_css": b__TRIPLE_QUOTE_PLACEHOLDER__$KATEX_CSS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "marked_js": b__TRIPLE_QUOTE_PLACEHOLDER__$MARKED_JS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "markdown_it_js": b__TRIPLE_QUOTE_PLACEHOLDER__$MARKDOWN_IT_JS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "prism_js": b__TRIPLE_QUOTE_PLACEHOLDER__$PRISM_JS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "katex_js": b__TRIPLE_QUOTE_PLACEHOLDER__$KATEX_JS_B64__TRIPLE_QUOTE_PLACEHOLDER__,
    "mermaid_js": b__TRIPLE_QUOTE_PLACEHOLDER__$MERMAID_JS_B64__TRIPLE_QUOTE_PLACEHOLDER__
}

def get_asset(name):
    content = ASSETS.get(name, b"")
    if not content or content.startswith(b"$"):
        return ""
    try:
        decoded = base64.b64decode(content)
        return gzip.decompress(decoded).decode('utf-8')
    except Exception as e:
        return f"/* Error decompression asset {name}: {str(e)} */"

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
        parent_path = os.path.dirname(base_path)
        if os.path.exists(os.path.join(parent_path, relative_path)):
            return os.path.join(parent_path, relative_path)
    return os.path.join(base_path, relative_path)

def get_icon_base64(icon_path):
    import base64
    if os.path.exists(icon_path):
        try:
            with open(icon_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception:
            pass
    return ""


HTML_TEMPLATE = __TRIPLE_QUOTE_PLACEHOLDER__<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PMDV Markdown Viewer</title>
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-glass: rgba(15, 23, 42, 0.65);
            --border-glass: rgba(255, 255, 255, 0.08);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --sidebar-width: 260px;
            --glow-color: rgba(99, 102, 241, 0.2);
            --shadow-primary: rgba(0, 0, 0, 0.3);
        }
        
        [data-theme="light"] {
            --bg-primary: #f8fafc;
            --bg-secondary: #f1f5f9;
            --bg-glass: rgba(255, 255, 255, 0.7);
            --border-glass: rgba(15, 23, 42, 0.08);
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --accent-color: #4f46e5;
            --accent-hover: #4338ca;
            --glow-color: rgba(79, 70, 229, 0.1);
            --shadow-primary: rgba(0, 0, 0, 0.05);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            transition: background-color 0.25s ease, color 0.25s ease, border-color 0.25s ease;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            display: flex;
            height: 100vh;
            overflow: hidden;
        }

        .sidebar {
            width: var(--sidebar-width);
            background: var(--bg-glass);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-right: 1px solid var(--border-glass);
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 28px;
            z-index: 10;
            box-shadow: 2px 0 15px var(--shadow-primary);
        }

        .brand {
            display: flex;
            flex-direction: row;
            align-items: center;
            justify-content: flex-start;
            gap: 12px;
            font-weight: 700;
            font-size: 15px;
            background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }

        .brand-icon {
            width: 32px;
            height: 32px;
            background: linear-gradient(135deg, #6366f1, #4f46e5);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 800;
            font-size: 16px;
            -webkit-text-fill-color: white;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
        }
        .menu-title {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
            font-weight: 700;
            margin-bottom: 10px;
        }

        .menu-group {
            display: flex;
            flex-direction: column;
        }

        .control-panel {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .control-label {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        select {
            width: 100%;
            background-color: var(--bg-primary);
            border: 1px solid var(--border-glass);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            outline: none;
        }

        select:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px var(--glow-color);
        }

        .status-container {
            margin-top: auto;
            background: var(--bg-secondary);
            border: 1px solid var(--border-glass);
            border-radius: 12px;
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .status-light {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background-color: #10b981;
            position: relative;
        }

        .status-light.syncing {
            background-color: #f59e0b;
        }

        .status-light.syncing::after {
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: inherit;
            animation: pulse 1.2s infinite;
        }

        .status-light.error {
            background-color: #ef4444;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.8; }
            100% { transform: scale(2.2); opacity: 0; }
        }

        .status-desc {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .workspace {
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
        }

        .header {
            height: 64px;
            border-bottom: 1px solid var(--border-glass);
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 32px;
            background: var(--bg-glass);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }

        .doc-info {
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            font-size: 15px;
        }

        .theme-toggle-btn {
            background: none;
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 18px;
        }

        .theme-toggle-btn:hover {
            background-color: var(--bg-secondary);
        }

        .viewer-area {
            flex: 1;
            overflow-y: auto;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            scroll-behavior: smooth;
        }

        .markdown-body {
            width: 100%;
            max-width: 820px;
            padding: 32px;
            border-radius: 16px;
            background-color: transparent !important;
            color: var(--text-primary) !important;
        }

        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        ::-webkit-scrollbar-track {
            background: transparent;
        }
        ::-webkit-scrollbar-thumb {
            background: var(--border-glass);
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--text-secondary);
        }

        [data-theme="dark"] .markdown-body {
            --color-canvas-default: transparent !important;
            --color-fg-default: #e2e8f0 !important;
            --color-fg-muted: #94a3b8 !important;
            --color-border-default: #334155 !important;
            --color-border-muted: #1e293b !important;
            --color-canvas-subtle: #1e293b !important;
            --color-neutral-muted: rgba(51, 65, 85, 0.4) !important;
            --color-accent-fg: #818cf8 !important;
        }
        
        [data-theme="light"] .markdown-body {
            --color-canvas-default: transparent !important;
            --color-fg-default: #0f172a !important;
            --color-fg-muted: #475569 !important;
            --color-border-default: #e2e8f0 !important;
            --color-border-muted: #f1f5f9 !important;
            --color-canvas-subtle: #f8fafc !important;
            --color-neutral-muted: rgba(226, 232, 240, 0.5) !important;
            --color-accent-fg: #4f46e5 !important;
        }

        /* File Open and Dropzone styles */
        .btn-primary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 10px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: background-color 0.2s, transform 0.1s;
            box-shadow: 0 4px 12px var(--glow-color);
        }
        .btn-primary:hover {
            background: var(--accent-hover);
        }
        .btn-primary:active {
            transform: scale(0.98);
        }
        .btn-secondary {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-glass);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
            transition: all 0.2s;
        }
        .btn-secondary:hover {
            background: var(--border-glass);
        }
        
        .dropzone-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            z-index: 100;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.25s ease;
            border: 3px dashed var(--accent-color);
            border-radius: 16px;
            margin: 10px;
            box-sizing: border-box;
            width: calc(100% - 20px);
            height: calc(100% - 20px);
        }
        .dropzone-overlay.active {
            opacity: 1;
            pointer-events: auto;
        }
        .dropzone-title {
            font-size: 24px;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 8px;
        }
        .dropzone-subtitle {
            font-size: 14px;
            color: var(--text-secondary);
        }
    
        /* Theme toggle SVG display rules */
        .theme-icon-sun, .theme-icon-moon {
            transition: transform 0.3s ease;
        }
        .theme-toggle-btn:hover .theme-icon-sun,
        .theme-toggle-btn:hover .theme-icon-moon {
            transform: rotate(20deg);
        }
        [data-theme="dark"] .theme-icon-sun {
            display: none;
        }
        [data-theme="dark"] .theme-icon-moon {
            display: block;
        }
        [data-theme="light"] .theme-icon-sun {
            display: block;
        }
        [data-theme="light"] .theme-icon-moon {
            display: none;
        }
    </style>
    
    <style id="lib-github-css"></style>
    <style id="lib-prism-css"></style>
    <style id="lib-katex-css"></style>
</head>
<body>
    <div class="sidebar">
        <div class="brand">
            <img src="data:image/png;base64,$BRAND_ICON_BASE64" alt="PMDV Logo" style="width: 40px; height: 40px; border-radius: 8px; box-shadow: 0 4px 12px var(--glow-color); object-fit: contain; background: transparent;">
            <span style="text-align: left; line-height: 1.2;">Portable<br>MD Viewer</span>
        </div>

        <div class="menu-group">
            <div class="menu-title">Markdown Engine</div>
            <div class="control-panel">
                <span class="control-label">Current Engine</span>
                <select id="engine-select">
                    <option value="marked">Marked.js (Fast)</option>
                    <option value="markdown-it">Markdown-it (Standard)</option>
                </select>
            </div>
        </div>

        <div class="menu-group">
            <div class="menu-title">Preference</div>
            <div class="control-panel">
                <span class="control-label">Theme Mode</span>
                <select id="theme-select">
                    <option value="dark">Dark Theme</option>
                    <option value="light">Light Theme</option>
                </select>
            </div>
        </div>

        <div class="menu-group">
            <div class="menu-title">Local File</div>
            <div class="control-panel">
                <input type="file" id="file-input" accept=".md,.markdown,.txt" style="display:none;">
                <button class="btn-primary" id="btn-open-file">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                    Open Local File...
                </button>
                <button class="btn-secondary" id="btn-reset-server" style="display:none;">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 4px;"><path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path></svg>
                    Reload Server File
                </button>
            </div>
        </div>

        <div class="status-container">
            <div class="status-light" id="status-dot"></div>
            <div class="status-desc" id="status-text">Synced</div>
        </div>
    </div>
    <div class="workspace" style="position: relative;">
        <div class="dropzone-overlay" id="dropzone">
            <div class="dropzone-title">Drop Markdown File</div>
            <div class="dropzone-subtitle">Release to view the document instantly</div>
        </div>
        <div class="header">
            <div class="doc-info">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="color: var(--text-secondary); margin-right: 4px;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                <span id="doc-title">Loading...</span>
            </div>
            <button class="theme-toggle-btn" id="theme-toggle" title="Toggle Theme">
                <svg class="theme-icon-sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>
                <svg class="theme-icon-moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>
            </button>
        </div>
        <div class="viewer-area" id="scroll-container">
            <article class="markdown-body" id="viewer-body">
            </article>
        </div>
    </div>

    <script id="lib-marked-js"></script>
    <script id="lib-markdown-it-js"></script>
    <script id="lib-prism-js"></script>
    <script id="lib-katex-js"></script>

    <script>
        // JS Console and Unhandled Exception Logging Bridge
        function logToPython(type, msg, extra = "") {
            if (window.pywebview && window.pywebview.api && window.pywebview.api.log_js_message) {
                window.pywebview.api.log_js_message(type, msg, extra);
            } else {
                console.log(`[JS-${type}]`, msg, extra);
            }
        }

        window.onerror = function(message, source, lineno, colno, error) {
            const errStr = `${message} at ${source}:${lineno}:${colno}`;
            logToPython("error", "Unhandled Exception: " + errStr, error ? error.stack : "");
            return false;
        };

        const originalConsoleError = console.error;
        console.error = function(...args) {
            logToPython("error", "Console Error: " + args.join(" "));
            originalConsoleError.apply(console, args);
        };

        const originalConsoleLog = console.log;
        console.log = function(...args) {
            logToPython("info", "Console Log: " + args.join(" "));
            originalConsoleLog.apply(console, args);
        };

        document.getElementById('lib-github-css').textContent = `$GITHUB_CSS`;
        document.getElementById('lib-prism-css').textContent = `$PRISM_CSS`;
        document.getElementById('lib-katex-css').textContent = `$KATEX_CSS`;
        
        function injectScript(id, code) {
            if (!code) return;
            const script = document.createElement('script');
            script.textContent = code;
            document.body.appendChild(script);
        }

        // Asynchronously load heavy assets through pywebview API to bypass NavigateToString limit
        async function loadAssetsAndInit() {
            try {
                if (window.pywebview && window.pywebview.api) {
                    setSyncStatus('syncing', 'Loading modules...');
                    
                    const markedCode = await window.pywebview.api.get_asset("marked_js");
                    injectScript('marked-run', markedCode);

                    const markdownItCode = await window.pywebview.api.get_asset("markdown_it_js");
                    injectScript('markdown-it-run', markdownItCode);

                    const prismCode = await window.pywebview.api.get_asset("prism_js");
                    injectScript('prism-run', prismCode);

                    const katexCode = await window.pywebview.api.get_asset("katex_js");
                    injectScript('katex-run', katexCode);

                    const mermaidCode = await window.pywebview.api.get_asset("mermaid_js");
                    injectScript('mermaid-run', mermaidCode);

                    setSyncStatus('success', 'Modules loaded');
                    
                    // Fetch initial content
                    const data = await window.pywebview.api.get_server_content();
                    window.updateFromServer(data);
                } else {
                    // Fallback for direct browser testing without bridge
                    setTimeout(renderMarkdown, 50);
                }
            } catch (err) {
                console.error("Asset load failed:", err);
                setSyncStatus('error', 'Module Load Error');
            }
        }

        const docTitle = document.getElementById('doc-title');
        const viewerBody = document.getElementById('viewer-body');
        const themeSelect = document.getElementById('theme-select');
        const themeToggle = document.getElementById('theme-toggle');
        const engineSelect = document.getElementById('engine-select');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');
        const fileInput = document.getElementById('file-input');
        const btnOpenFile = document.getElementById('btn-open-file');
        const btnResetServer = document.getElementById('btn-reset-server');
        const dropzone = document.getElementById('dropzone');

        // Safe localStorage wrapper for about:blank security sandboxing
        let safeLocalStorage;
        try {
            safeLocalStorage = window.localStorage;
            if (safeLocalStorage) {
                safeLocalStorage.getItem('test');
            } else {
                throw new Error("localStorage is null");
            }
        } catch (e) {
            const memoryStorage = {};
            safeLocalStorage = {
                getItem: (key) => memoryStorage[key] || null,
                setItem: (key, value) => { memoryStorage[key] = String(value); },
                removeItem: (key) => { delete memoryStorage[key]; },
                clear: () => { for (let k in memoryStorage) delete memoryStorage[k]; }
            };
        }

        let rawMarkdown = "";
        let currentTheme = safeLocalStorage.getItem('theme') || 'dark';
        let currentEngine = safeLocalStorage.getItem('engine') || 'marked';

        themeSelect.value = currentTheme;
        engineSelect.value = currentEngine;
        applyTheme(currentTheme);

        let isLocalMode = false;


        
        function parseAndRenderLaTeX(element) {
            if (typeof katex === 'undefined') return;

            const walk = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
            const textNodes = [];
            while(walk.nextNode()) textNodes.push(walk.currentNode);

            textNodes.forEach(node => {
                let text = node.nodeValue;
                if (!text) return;

                if (text.includes('$')) {
                    const span = document.createElement('span');
                    let hasFormula = false;
                    
                    let segments = text.split(/(\\$\\$[\\s\\S]+?\\$\\$|\\$[\\s\\S]+?\\$)/g);
                    
                    segments.forEach(seg => {
                        if (seg.startsWith('$$') && seg.endsWith('$$')) {
                            hasFormula = true;
                            const formula = seg.slice(2, -2);
                            const mathSpan = document.createElement('div');
                            mathSpan.style.margin = '1em 0';
                            mathSpan.style.textAlign = 'center';
                            try {
                                katex.render(formula, mathSpan, { displayMode: true, throwOnError: false });
                                span.appendChild(mathSpan);
                            } catch (e) {
                                span.appendChild(document.createTextNode(seg));
                            }
                        } else if (seg.startsWith('$') && seg.endsWith('$')) {
                            hasFormula = true;
                            const formula = seg.slice(1, -1);
                            const mathSpan = document.createElement('span');
                            try {
                                katex.render(formula, mathSpan, { displayMode: false, throwOnError: false });
                                span.appendChild(mathSpan);
                            } catch (e) {
                                span.appendChild(document.createTextNode(seg));
                            }
                        } else {
                            span.appendChild(document.createTextNode(seg));
                        }
                    });

                    if (hasFormula) {
                        node.parentNode.replaceChild(span, node);
                    }
                }
            });
        }
        
        function renderMarkdown() {
            if (!rawMarkdown) return;
            
            try {
                let html = "";
                if (currentEngine === 'markdown-it') {
                    if (typeof markdownit !== 'undefined') {
                        html = window.markdownit({
                            html: true,
                            linkify: true,
                            typographer: true,
                            breaks: true
                        }).render(rawMarkdown);
                    } else {
                        html = "<p style='color:red;'>Error: markdown-it was not loaded properly.</p>" + marked.parse(rawMarkdown, { breaks: true });
                    }
                } else {
                    html = marked.parse(rawMarkdown, { breaks: true });
                }

                viewerBody.innerHTML = html;
                
                if (typeof Prism !== 'undefined') {
                    Prism.highlightAllUnder(viewerBody);
                }

                // Render Mermaid Diagrams if available
                if (window.mermaid) {
                    try {
                        const mermaidNodes = viewerBody.querySelectorAll('.language-mermaid');
                        mermaidNodes.forEach((node, idx) => {
                            if (!node.parentNode) return; // Prevent crashes when duplicate queries fetch detached nodes
                            
                            const code = node.textContent;
                            const container = document.createElement('div');
                            container.className = 'mermaid';
                            container.id = 'mermaid-' + idx;
                            container.textContent = code;
                            
                            let target = node;
                            if (node.parentNode && node.parentNode.tagName === 'PRE') {
                                target = node.parentNode;
                            }
                            
                            if (target.parentNode) {
                                target.parentNode.replaceChild(container, target);
                            }
                        });
                        
                        mermaid.initialize({
                            startOnLoad: false,
                            theme: currentTheme === 'dark' ? 'dark' : 'default',
                            securityLevel: 'loose'
                        });
                        mermaid.init(undefined, viewerBody.querySelectorAll('.mermaid'));
                    } catch (e) {
                        console.error('Mermaid render error:', e);
                    }
                }
                
                parseAndRenderLaTeX(viewerBody);
                
                setSyncStatus('success', 'Synced');
            } catch (err) {
                console.error(err);
                viewerBody.innerHTML = `<div style="padding:20px; border:1px solid #f87171; background:rgba(239,68,68,0.1); border-radius:8px; color:#ef4444;">
                    <strong>Rendering Error:</strong><br>\\${err.message}
                </div>` + viewerBody.innerHTML;
                setSyncStatus('error', 'Render Error');
            }
        }

        function setSyncStatus(status, text) {
            statusDot.className = 'status-light';
            if (status === 'syncing') {
                statusDot.classList.add('syncing');
            } else if (status === 'error') {
                statusDot.classList.add('error');
            }
            statusText.textContent = text;
        }

        function applyTheme(theme) {
            document.body.setAttribute('data-theme', theme);
            safeLocalStorage.setItem('theme', theme);
            currentTheme = theme;
            themeSelect.value = theme;
        }

        // Global hook invoked from Python watcher thread
        window.updateFromServer = function(data) {
            if (isLocalMode) return;
            docTitle.textContent = data.filename;
            document.title = "PMDV - Portable Markdown Viewer";
            rawMarkdown = data.content;
            renderMarkdown();
            setSyncStatus('success', 'Synced');
        };

        function handleLocalFile(file) {
            if (!file) return;
            const reader = new FileReader();
            reader.onload = function(e) {
                isLocalMode = true;
                docTitle.textContent = file.name;
                document.title = "PMDV - Portable Markdown Viewer";
                rawMarkdown = e.target.result;
                renderMarkdown();
                setSyncStatus('success', 'Loaded Local File');
                btnResetServer.style.display = 'inline-flex';
            };
            reader.onerror = function() {
                setSyncStatus('error', 'Read Local Error');
            };
            reader.readAsText(file);
        }

        btnOpenFile.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleLocalFile(e.target.files[0]);
            }
        });

        // Drag & Drop Handlers
        let dragCounter = 0;
        window.addEventListener('dragenter', (e) => {
            e.preventDefault();
            dragCounter++;
            if (dragCounter === 1) {
                dropzone.classList.add('active');
            }
        });
        window.addEventListener('dragover', (e) => {
            e.preventDefault();
        });
        window.addEventListener('dragleave', (e) => {
            e.preventDefault();
            dragCounter--;
            if (dragCounter === 0) {
                dropzone.classList.remove('active');
            }
        });
        window.addEventListener('drop', (e) => {
            e.preventDefault();
            dragCounter = 0;
            dropzone.classList.remove('active');
            if (e.dataTransfer.files.length > 0) {
                const file = e.dataTransfer.files[0];
                if (file.name.endsWith('.md') || file.name.endsWith('.markdown') || file.name.endsWith('.txt')) {
                    handleLocalFile(file);
                } else {
                    alert('Only Markdown (.md, .markdown) or Text (.txt) files are supported.');
                }
            }
        });

        btnResetServer.addEventListener('click', () => {
            isLocalMode = false;
            btnResetServer.style.display = 'none';
            fileInput.value = '';
            setSyncStatus('syncing', 'Updating...');
            if (window.pywebview && window.pywebview.api) {
                window.pywebview.api.get_server_content().then(data => {
                    window.updateFromServer(data);
                }).catch(err => {
                    setSyncStatus('error', 'API Bridge Error');
                });
            }
        });

        themeToggle.addEventListener('click', () => {
            applyTheme(currentTheme === 'dark' ? 'light' : 'dark');
        });
        themeSelect.addEventListener('change', (e) => {
            applyTheme(e.target.value);
        });

        engineSelect.addEventListener('change', (e) => {
            currentEngine = e.target.value;
            safeLocalStorage.setItem('engine', currentEngine);
            setSyncStatus('syncing', 'Re-rendering...');
            setTimeout(renderMarkdown, 50);
        });

        // Handle initialization
        if (window.pywebview) {
            loadAssetsAndInit();
        } else {
            window.addEventListener('pywebviewready', () => {
                loadAssetsAndInit();
            });
            setTimeout(() => {
                if (typeof window.pywebview === 'undefined') {
                    renderMarkdown();
                }
            }, 1000);
        }
    </script>
</body>
</html>
__TRIPLE_QUOTE_PLACEHOLDER__


class ViewerApi:
    def __init__(self, markdown_file_path):
        self.markdown_file_path = os.path.abspath(markdown_file_path)

    def get_asset(self, name):
        try:
            return get_asset(name)
        except Exception as e:
            return f"/* API asset load error {name}: {str(e)} */"

    def log_js_message(self, log_type, message, extra=""):
        sys.stderr.write(f"[JS {log_type.upper()}] {message}\n")
        if extra:
            sys.stderr.write(f"Detail: {extra}\n")
        sys.stderr.flush()

    def get_server_content(self):
        filepath = self.markdown_file_path
        filename = os.path.basename(filepath)
        content = ""
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                content = f"# Error reading file\\n\\n{str(e)}"
        else:
            content = f"# File not found\\n\\nPath: `{filepath}`"
            
        return {
            "filename": filename,
            "content": content
        }

def watch_loop(window, api):
    filepath = api.markdown_file_path
    last_mtime = 0
    if os.path.exists(filepath):
        last_mtime = os.path.getmtime(filepath)
        
    while True:
        time.sleep(0.5)
        if not os.path.exists(filepath):
            continue
        try:
            current_mtime = os.path.getmtime(filepath)
            if current_mtime != last_mtime:
                last_mtime = current_mtime
                data = api.get_server_content()
                payload = json.dumps(data)
                window.evaluate_js(f"window.updateFromServer({payload})")
        except Exception:
            pass

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == '--init':
        python_path = sys.executable
        script_path = os.path.abspath(__file__)
        alias_line = f'alias pmdv="{python_path} {script_path}"'
        print(alias_line)
        shell = os.environ.get("SHELL", "")
        home = os.path.expanduser("~")
        rc_file = None
        if "zsh" in shell:
            rc_file = os.path.join(home, ".zshrc")
        elif "bash" in shell:
            rc_file = os.path.join(home, ".bashrc")
        if rc_file and os.path.exists(rc_file):
            try:
                with open(rc_file, "r", encoding="utf-8") as f:
                    content = f.read()
                if "alias pmdv=" not in content:
                    with open(rc_file, "a", encoding="utf-8") as f:
                        f.write(f"\\n# Added by PMDV Init\\n{alias_line}\\n")
                    sys.stderr.write(f"[Init] Permanently added alias to {rc_file}\\n")
                else:
                    sys.stderr.write(f"[Init] Alias pmdv already exists in {rc_file}\\n")
            except Exception as e:
                sys.stderr.write(f"[Init] Failed to write to shell config: {e}\\n")
        sys.exit(0)

    if len(sys.argv) < 2:
        print("Usage: python viewer.py <path-to-markdown-file>")
        md_files = [f for f in os.listdir('.') if f.endswith('.md')]
        if md_files:
            target = md_files[0]
            print(f"No file specified. Defaulting to first found: {target}")
        else:
            target = 'README.md'
            if not os.path.exists(target):
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(__TRIPLE_QUOTE_PLACEHOLDER__# PMDV - Portable Markdown Viewer

Welcome to your offline Markdown viewer!

### Key Features
- **100% Offline**: All scripts, styles, and rendering libraries are bundled into this single binary.
- **Rich Syntax Support**: LaTeX math formulas ($E=mc^2$), code highlighting (Prism), and vector charts (Mermaid).
- **Real-Time Watcher**: Detects local file modification instantly and hot-reloads the view.
- **Portless Execution**: Uses pywebview IPC bindings directly rather than spinning up local web servers.__TRIPLE_QUOTE_PLACEHOLDER__)
            print(f"No file specified. Created dummy target: {target}")
    else:
        target = sys.argv[1]

    api = ViewerApi(target)
    
    # Resolve and load icon asset
    icon_path = get_resource_path("icon.png")
    icon_base64 = get_icon_base64(icon_path)
    
    html_content = HTML_TEMPLATE
    html_content = html_content.replace("$BRAND_ICON_BASE64", icon_base64)
    html_content = html_content.replace("$GITHUB_CSS", get_asset("github_css"))
    html_content = html_content.replace("$PRISM_CSS", get_asset("prism_css"))
    html_content = html_content.replace("$KATEX_CSS", get_asset("katex_css"))
    
    title = "PMDV - Portable Markdown Viewer"
    window = webview.create_window(title, html=html_content, js_api=api, width=1200, height=800, text_select=True)
    
    def on_window_ready():
        # Start file watch thread
        watcher_thread = threading.Thread(target=watch_loop, args=(window, api), daemon=True)
        watcher_thread.start()

    webview.start(on_window_ready, debug=False)

if __name__ == '__main__':
    main()
"""

def download_assets():
    assets_b64 = {}
    print("Starting assets downloading...")
    for name, url in ASSET_URLS.items():
        print(f"Downloading {name} from {url}...")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                content = response.read()
                compressed = gzip.compress(content)
                encoded = base64.b64encode(compressed).decode('utf-8')
                assets_b64[name] = encoded
        except Exception as e:
            print(f"Failed to download {name}: {e}")
            sys.exit(1)
    return assets_b64

def main():
    assets = download_assets()
    template = VIEWER_TEMPLATE
    
    for name, b64 in assets.items():
        placeholder = f"${name.upper()}_B64"
        template = template.replace(placeholder, b64)
        
    # Revert alphanumeric placeholder back to valid Python triple quotes
    template = template.replace('__TRIPLE_QUOTE_PLACEHOLDER__', '"""')
        
    # Check output path
    if os.path.exists("pmdv"):
        out_dir = os.path.join("pmdv", "viewer.py")
        if os.path.exists(os.path.join("pmdv", "pmdv")):
            out_dir = os.path.join("pmdv", "pmdv", "viewer.py")
    else:
        out_dir = "viewer.py"
        
    with open(out_dir, "w", encoding="utf-8") as f:
        f.write(template)
    print(f"Generated standalone self-contained {os.path.abspath(out_dir)} successfully!")

if __name__ == '__main__':
    main()
