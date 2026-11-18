import json
import os
import sys

import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "case_and_connect_wholesalers.settings"
)
django.setup()

from django.db import transaction
from products.models import Product

with open(
    os.environ.get("ORIGINAL_PRODUCTS_FILE", "all_products.json"),
    encoding="utf-8-sig"
) as file:
    original = json.load(file)


with open(
    os.environ.get("PRODUCT_UPDATES_FILE", "product_updates.json"),
    encoding="utf-8"
) as file:
    updates = json.load(file)


original_names = {
    item["pk"]: item["fields"]["name"]
    for item in original
}

update_map = {
    item["id"]: item
    for item in updates
}

live_products = {
    product.pk: product
    for product in Product.objects.all()
}

# Stop if product IDs or original names do not match.
if (
    len(original) != 37
    or len(updates) != 37
    or len(update_map) != 37
    or set(original_names) != set(update_map)
    or set(original_names) != set(live_products)
    or any(
        live_products[pk].name != name
        for pk, name in original_names.items()
    )
):
    sys.exit("STOP: Product records do not match.")

# Only make changes when explicitly confirmed.
if "--apply" not in sys.argv:
    print("Safety checks passed for all 37 products.")
    print("DRY RUN: No database changes made.")
    sys.exit()

with transaction.atomic():
    for pk, data in update_map.items():
        product = live_products[pk]
        product.name = data["name"]
        product.description = data["description"]
        product.price = data["price"]

        product.save(
            update_fields=["name", "description", "price"]
        )

print("SUCCESS: All 37 products updated.")
