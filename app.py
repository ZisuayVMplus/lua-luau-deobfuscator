from flask import Flask, render_template, request, send_file, jsonify
from io import BytesIO
from deobfuscator import deobfuscate

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/deobfuscate")
def api_deobfuscate():
    upload = request.files.get("file")
    if not upload:
        return jsonify({"error": "No file uploaded"}), 400
    try:
        raw = upload.read().decode("utf-8", errors="replace")
        result = deobfuscate(raw)
        return jsonify({
            "filename": upload.filename or "input.lua",
            "output": result["code"],
            "stats": result["stats"],
            "warnings": result["warnings"],
        })
    except Exception as exc:
        return jsonify({"error": f"Deobfuscation failed: {exc}"}), 500

@app.post("/api/download")
def api_download():
    data = request.get_json(force=True)
    code = data.get("code", "")
    filename = data.get("filename", "deobfuscated.lua")
    if not filename.lower().endswith(".lua"):
        filename += ".lua"
    return send_file(
        BytesIO(code.encode("utf-8")),
        mimetype="text/plain; charset=utf-8",
        as_attachment=True,
        download_name=filename,
    )

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
