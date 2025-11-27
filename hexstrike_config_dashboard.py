import http.server
import socketserver
import json
import os
import webbrowser
import sys

PORT = 8080
CONFIG_FILE = "mcp_tool_config.json"
CATEGORIES_FILE = "tool_categories.json"

class ConfigHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_html_content().encode("utf-8"))
        elif self.path == "/api/config":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            config = self.load_config()
            categories = self.load_categories()
            response_data = {
                "config": config,
                "categories": categories
            }
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/api/config":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                new_config = json.loads(post_data.decode("utf-8"))
                self.save_config(new_config)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self.send_error(404)

    def load_config(self):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {"enabled_tools": []}

    def save_config(self, config):
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)

    def load_categories(self):
        try:
            with open(CATEGORIES_FILE, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def get_html_content(self):
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HexStrike MCP Tool Manager</title>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --text-color: #c9d1d9;
            --accent-color: #58a6ff;
            --border-color: #30363d;
            --success-color: #238636;
            --danger-color: #da3633;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 20px;
        }
        h1 {
            margin: 0;
            font-size: 24px;
            color: var(--accent-color);
        }
        .actions {
            display: flex;
            gap: 10px;
        }
        button {
            padding: 8px 16px;
            border-radius: 6px;
            border: 1px solid var(--border-color);
            background-color: var(--card-bg);
            color: var(--text-color);
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.2s;
        }
        button:hover {
            background-color: #21262d;
        }
        button.primary {
            background-color: var(--success-color);
            border-color: var(--success-color);
            color: white;
            font-weight: bold;
        }
        button.primary:hover {
            background-color: #2ea043;
        }
        .search-bar {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: var(--text-color);
            font-size: 16px;
        }
        .category-section {
            margin-bottom: 30px;
        }
        .category-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .category-title {
            font-size: 18px;
            font-weight: bold;
            color: var(--text-color);
        }
        .tool-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
        }
        .tool-card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 15px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: border-color 0.2s;
        }
        .tool-card:hover {
            border-color: var(--accent-color);
        }
        .tool-info {
            display: flex;
            flex-direction: column;
        }
        .tool-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .tool-status {
            font-size: 12px;
            color: #8b949e;
        }
        /* Toggle Switch */
        .switch {
            position: relative;
            display: inline-block;
            width: 40px;
            height: 20px;
        }
        .switch input {
            opacity: 0;
            width: 0;
            height: 0;
        }
        .slider {
            position: absolute;
            cursor: pointer;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: #30363d;
            transition: .4s;
            border-radius: 20px;
        }
        .slider:before {
            position: absolute;
            content: "";
            height: 16px;
            width: 16px;
            left: 2px;
            bottom: 2px;
            background-color: white;
            transition: .4s;
            border-radius: 50%;
        }
        input:checked + .slider {
            background-color: var(--success-color);
        }
        input:checked + .slider:before {
            transform: translateX(20px);
        }
        .stats {
            margin-top: 5px;
            font-size: 14px;
            color: #8b949e;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background-color: var(--success-color);
            color: white;
            padding: 10px 20px;
            border-radius: 6px;
            display: none;
            animation: fadeIn 0.3s, fadeOut 0.3s 2.7s;
        }
        @keyframes fadeIn { from {opacity: 0;} to {opacity: 1;} }
        @keyframes fadeOut { from {opacity: 1;} to {opacity: 0;} }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>HexStrike MCP Tool Manager</h1>
                <div class="stats" id="stats">Enabled: 0 / 0</div>
            </div>
            <div class="actions">
                <button onclick="saveConfig()" class="primary">Save Configuration</button>
            </div>
        </header>

        <input type="text" class="search-bar" placeholder="Search tools..." onkeyup="filterTools(this.value)">

        <div id="content"></div>
    </div>

    <div id="toast" class="toast">Configuration Saved!</div>

    <script>
        let currentConfig = { enabled_tools: [] };
        let categories = {};

        async function loadData() {
            const response = await fetch('/api/config');
            const data = await response.json();
            currentConfig = data.config;
            categories = data.categories;
            render();
        }

        function render() {
            const content = document.getElementById('content');
            content.innerHTML = '';
            
            let totalTools = 0;
            let enabledCount = 0;

            for (const [category, tools] of Object.entries(categories)) {
                const section = document.createElement('div');
                section.className = 'category-section';
                
                const header = document.createElement('div');
                header.className = 'category-header';
                header.innerHTML = `
                    <span class="category-title">${category.replace(/_/g, ' ')}</span>
                    <div>
                        <button onclick="toggleCategory('${category}', true)">Select All</button>
                        <button onclick="toggleCategory('${category}', false)">Deselect All</button>
                    </div>
                `;
                section.appendChild(header);

                const grid = document.createElement('div');
                grid.className = 'tool-grid';

                tools.forEach(tool => {
                    totalTools++;
                    const isEnabled = currentConfig.enabled_tools.includes(tool);
                    if (isEnabled) enabledCount++;

                    const card = document.createElement('div');
                    card.className = 'tool-card';
                    card.dataset.name = tool.toLowerCase();
                    card.innerHTML = `
                        <div class="tool-info">
                            <span class="tool-name">${tool}</span>
                            <span class="tool-status">${isEnabled ? 'Enabled' : 'Disabled'}</span>
                        </div>
                        <label class="switch">
                            <input type="checkbox" ${isEnabled ? 'checked' : ''} 
                                onchange="toggleTool('${tool}', this.checked)">
                            <span class="slider"></span>
                        </label>
                    `;
                    grid.appendChild(card);
                });

                section.appendChild(grid);
                content.appendChild(section);
            }

            document.getElementById('stats').textContent = `Enabled: ${enabledCount} / ${totalTools}`;
        }

        function toggleTool(tool, enabled) {
            if (enabled) {
                if (!currentConfig.enabled_tools.includes(tool)) {
                    currentConfig.enabled_tools.push(tool);
                }
            } else {
                currentConfig.enabled_tools = currentConfig.enabled_tools.filter(t => t !== tool);
            }
            render();
        }

        function toggleCategory(category, enable) {
            const tools = categories[category];
            tools.forEach(tool => {
                if (enable) {
                    if (!currentConfig.enabled_tools.includes(tool)) {
                        currentConfig.enabled_tools.push(tool);
                    }
                } else {
                    currentConfig.enabled_tools = currentConfig.enabled_tools.filter(t => t !== tool);
                }
            });
            render();
        }

        function filterTools(query) {
            const cards = document.querySelectorAll('.tool-card');
            query = query.toLowerCase();
            
            cards.forEach(card => {
                const name = card.dataset.name;
                if (name.includes(query)) {
                    card.style.display = 'flex';
                } else {
                    card.style.display = 'none';
                }
            });
        }

        async function saveConfig() {
            try {
                const response = await fetch('/api/config', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(currentConfig)
                });
                
                if (response.ok) {
                    showToast();
                } else {
                    alert('Failed to save configuration');
                }
            } catch (e) {
                alert('Error saving configuration: ' + e);
            }
        }

        function showToast() {
            const toast = document.getElementById('toast');
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }

        loadData();
    </script>
</body>
</html>
        """

if __name__ == "__main__":
    Handler = ConfigHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Opening browser...")
        webbrowser.open(f"http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()
