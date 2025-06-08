# 🦙 Gedit Local LLaMA Plugin

> ✨ AI in your text editor. Streamlined. Local. No cloud fluff. No API keys. Just raw power.

**Gedit Local LLaMA** is a lightweight yet powerful plugin that brings the strength of locally running [Ollama](https://ollama.com) models (like LLaMA, Mistral, DeepSeek, etc.) right into your Gedit context menu.

---

## ⚙️ Features

* 📝 **Summarize** selected text using your favorite local LLM.
* 🔮 **Generate** follow-up content, ideas, completions or rewrites.
* 📋 One-click **copy to clipboard** from modal output.
* 🔄 Fully **streaming** responses as they arrive.
* 🌀 **Loading spinner** and automatic scroll to latest text.
* 📑 Context menu integration with **quick actions** and **model selectors**.
* ⚡ Super-fast local inference with Ollama, no external API.

---

## 🔧 Requirements

* **Gedit** (tested on 40+)
* **Ollama** running locally ([https://ollama.com](https://ollama.com))
* Python packages:

  * `requests`
  * `gi` bindings (comes with Gedit on most distros)

---

## 🛠️ Installation

1. Clone or download this repo:

   ```bash
   git clone https://github.com/maifeeulasad/gedit-localllama.git
   ```

2. Copy the plugin into Gedit's plugin directory:

   ```bash
   chmod +x install.sh
   sudo ./install.sh
   ```

3. Restart Gedit.

4. Open Gedit > Preferences > Plugins, then **enable "GEdit Local Llama Plugin"**.

---

## 💡 Usage

1. Select some text in your Gedit document.
2. Right-click to open the context menu.
3. Choose from:

   * **🔮 Generate (model-name)**
   * **📝 Summarize (model-name)**
   * Or select from specific models under "Generate with..." or "Summarize with..."

Output will appear in a clean modal dialog. You can copy the result with one click.

---

## 🤖 Example Use Cases

| Task                    | What to Do                                  |
| ----------------------- | ------------------------------------------- |
| Rewrite a paragraph     | Select it → Right-click → Generate          |
| Summarize meeting notes | Select notes → Right-click → Summarize      |
| Draft email replies     | Select prompt → Generate                    |
| Run locally, forever    | No API tokens, no cloud bill, just freedom. |

---

## 🧠 About Ollama

You can install and run Ollama easily from their site:
👉 [https://ollama.com](https://ollama.com)

Start a model like:

```bash
ollama run llama3
```

Or pull a model:

```bash
ollama pull deepseek-coder
```

The plugin will automatically detect available models at `http://localhost:11434`.

---

## 🧪 Dev Notes

* You can extend this plugin to support chat history, embedding visual selectors, or even auto-generation via keystrokes.
* Gedit plugins are Python-based and hot-reload friendly.

---

## 👨‍💻 Author

**Maifee Ul Asad**
🔗 [GitHub](https://github.com/maifeeulasad)
🚀 Building fast, efficient, privacy-respecting tools for everyone.

---

## 📄 License

Gedit Local LLaMA Plugin
Copyright © 2025 [Maifee Ul Asad]

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.