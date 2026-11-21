import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal, InvalidOperation

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)
DB_PATH = Path(__file__).parent / "instance" / "bathfoodfinder.sqlite"

@app.get("/")
def home():
    return render_template("home.html")

@app.get("/listings")
def listings():
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with closing(sqlite3.connect(DB_PATH)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("""
    SELECT food_items.name, food_items.outlet, food_items.allergens,
           listings.price_pence, listings.portions, listings.collection_deadline
    FROM listings
    JOIN food_items ON food_items.id = listings.food_item_id
    WHERE listings.portions > 0
      AND listings.collection_deadline > ?
    ORDER BY listings.collection_deadline ASC, listings.id ASC
            """, (now,)).fetchall()

    offers = [
        {
            "name": row["name"],
            "price": f"{row['price_pence'] / 100:.2f}",
            "portions": row["portions"],
            "outlet": row["outlet"],
            "allergens": row["allergens"] or "Not recorded",
            "deadline": datetime.fromisoformat(
                row["collection_deadline"]
            ).astimezone().strftime("%H:%M"),
        }
        for row in rows
    ]
    return render_template("listings.html", offers=offers)

@app.get("/staff/listings/new")
def choose_food():
    with closing(sqlite3.connect(DB_PATH)) as db:
        db.row_factory = sqlite3.Row
        foods = db.execute(
    "SELECT id, name, outlet FROM food_items ORDER BY name, outlet").fetchall()

    return render_template("choose_food.html", foods=foods)


@app.get("/staff/listings/review")
def review_item():
    food_choice = request.args.get("food_choice", "").strip()

    with closing(sqlite3.connect(DB_PATH)) as db:
        db.row_factory = sqlite3.Row

        food = db.execute(
            """
            SELECT id, name, outlet, allergens
            FROM food_items
            WHERE name || ' - ' || outlet = ?
            """,
            (food_choice,),
        ).fetchone()

        if food is None:
            foods = db.execute(
                "SELECT id, name, outlet FROM food_items ORDER BY name, outlet"
            ).fetchall()

    if food is None:
        return render_template(
            "choose_food.html",
            foods=foods,
            food_choice=food_choice,
            error="Please select a valid food from the suggestions.",
        ), 400

    return render_template("review_item.html", food=food)
    

@app.post("/staff/listings/publish")
def publish_offer():
    try:
        food_id = int(request.form["food_item_id"])
        price = Decimal(request.form["price"])

        if not price.is_finite() or price.as_tuple().exponent < -2:
            raise ValueError

        price_pence = int(price * 100)

        portions = int(request.form["portions"])

        collection_time = datetime.strptime(request.form["deadline"], "%H:%M").time()
        deadline = datetime.combine(datetime.now().date(), collection_time)
        deadline = deadline.astimezone(timezone.utc)
    except (KeyError, ValueError, OverflowError, InvalidOperation):
        abort(400, "Enter a valid price, quantity and deadline.")

    if price < 0 or portions < 1:
        abort(400, "Enter a non-negative price and at least one portion.")

    if deadline <= datetime.now(timezone.utc):
        with closing(sqlite3.connect(DB_PATH)) as db:
            db.row_factory = sqlite3.Row
            food = db.execute(
                "SELECT id, name, outlet, allergens FROM food_items WHERE id = ?",
                (food_id,),
            ).fetchone()

        if food is None:
            return redirect(url_for("choose_food"))

        return render_template(
            "review_item.html",
            food=food,
            error="Please enter a collection time later than the current time.",
        ), 400

    with closing(sqlite3.connect(DB_PATH)) as db:
        db.execute("PRAGMA foreign_keys = ON")
        try:
            db.execute(
                """
                INSERT INTO listings
                    (food_item_id, price_pence, portions, collection_deadline)
                VALUES (?, ?, ?, ?)
                """,
                (food_id, price_pence, portions, deadline.isoformat(timespec="seconds")),
            )
            db.commit()
        except sqlite3.IntegrityError:
            abort(400, "Choose an item from the catalogue.")
        except OverflowError:
            abort(400, "One of the numbers is too large.")

    return redirect(url_for("listings", published="1"))