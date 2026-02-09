import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "trades.json")


def load_trades():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_trades(trades):
    with open(DATA_FILE, "w") as f:
        json.dump(trades, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/trades", methods=["GET"])
def get_trades():
    month = request.args.get("month")
    year = request.args.get("year")
    trades = load_trades()
    if month and year:
        trades = [
            t
            for t in trades
            if t["date"].startswith(f"{int(year):04d}-{int(month):02d}")
        ]
    return jsonify(trades)


@app.route("/api/trades", methods=["POST"])
def add_trade():
    trade = request.get_json()
    required = ["date", "asset", "operation", "result", "profit"]
    if not all(k in trade for k in required):
        return jsonify({"error": "Missing fields"}), 400
    trade.setdefault("entry_time", "")
    trade.setdefault("exit_time", "")
    trade.setdefault("rr_ratio", None)
    trade["profit"] = float(trade["profit"])
    if trade["result"] == "loss":
        trade["profit"] = -abs(trade["profit"])
    trades = load_trades()
    trade["id"] = max((t["id"] for t in trades), default=0) + 1
    trades.append(trade)
    save_trades(trades)
    return jsonify(trade), 201


@app.route("/api/trades/<int:trade_id>", methods=["DELETE"])
def delete_trade(trade_id):
    trades = load_trades()
    trades = [t for t in trades if t["id"] != trade_id]
    save_trades(trades)
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
