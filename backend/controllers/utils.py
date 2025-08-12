from flask import jsonify

def jsonify_ok(data=None):
    if data is None:
        return jsonify({"ok": True}), 200
    return jsonify({"ok": True, "result": data}), 200

def jsonify_error(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code
