from flask import jsonify

def success(data=None, message="OK", status=200):
    r = {"success": True, "message": message}
    if data is not None:
        r["data"] = data
    return jsonify(r), status

def error(message="Erreur", status=400, details=None):
    r = {"success": False, "message": message}
    if details:
        r["details"] = details
    return jsonify(r), status