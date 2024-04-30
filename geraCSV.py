import csv
import json

def convert_to_csv(json_filename, csv_filename):
    with open(json_filename, 'r', encoding='utf-8') as jsonfile:
        product_data_list = json.load(jsonfile)

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Product Type",
            "Tags", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
            "Variant SKU", "Variant Price", "Compare At Price", "Image Src", "Published",
            "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
            "Variant Fulfillment Service", "Variant Requires Shipping", "Variant Taxable",
            "Gift Card", "SEO Title", "SEO Description", "Status", "Collection"
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for product in product_data_list:
            product_name = product["product_name"]
            size = product["size"]
            handle = product_name.lower().replace(" ", "-")

            for photo in product["photos"]:
                image_url = "https:" + photo["image_url"]
                photo_title = photo["title"]

                writer.writerow({
                    "Handle": handle,
                    "Title": product_name,
                    "Body (HTML)": "<p>Beautiful Soccer Jersey</p>",
                    "Vendor": "Gobbis",
                    "Product Category": "Vestuário e acessórios > Roupas > Uniformes > Uniformes esportivos",
                    "Product Type": "Soccer, Jersey, 2024",
                    "Tags": "Soccer",
                    "Option1 Name": "Photo Title",
                    "Option1 Value": photo_title,
                    "Option2 Name": "Size",
                    "Option2 Value": size,
                    "Variant SKU": handle + '-' + photo_title[:10],
                    "Variant Price": "19.99",
                    "Compare At Price": "",
                    "Image Src": image_url,
                    "Published": "TRUE",
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": "100",
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Requires Shipping": "TRUE",
                    "Variant Taxable": "TRUE",
                    "Gift Card": "FALSE",
                    "SEO Title": product_name,
                    "SEO Description": "Purchase your 2024 Soccer Jerseys today!",
                    "Status": "active",
                    "Collection": "Soccer, Jersey, 2024"
                })

convert_to_csv('product_details.json', 'products.csv')
