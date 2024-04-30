import csv
import json

def convert_to_csv(json_filename, csv_filename):
    # Carregar dados do arquivo JSON
    with open(json_filename, 'r', encoding='utf-8') as jsonfile:
        product_data_list = json.load(jsonfile)

    # Criar ou abrir o arquivo CSV
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        # Definir os nomes das colunas
        fieldnames = [
            "Handle", "Title", "Body (HTML)", "Vendor", "Product Category", "Product Type",
            "Tags", "Option1 Name", "Option1 Value", "Option2 Name", "Option2 Value",
            "Variant SKU", "Variant Price", "Compare At Price", "Image Src", "Published",
            "Variant Inventory Tracker", "Variant Inventory Qty", "Variant Inventory Policy",
            "Variant Fulfillment Service", "Variant Requires Shipping", "Variant Taxable",
            "Gift Card", "SEO Title", "SEO Description", "Status", "Collection"
        ]

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Escrever o cabeçalho no arquivo CSV
        writer.writeheader()

        # Iterar sobre cada produto
        for product_data in product_data_list:
            # Definir o estoque baseado na disponibilidade do produto
            inventory_qty = "0" if product_data.get('ProdutoEsgotado', False) else "100"

            # Iterar sobre cada variação do produto e escrever no CSV
            for variation in product_data["Variações do produto"]:

                variant_price = "{:.2f}".format(product_data["Novo preço (150%)"])
                cor = variation.get('Nome da variação', 'N/A')
                tamanho = variation.get('Tamanho da variação', 'N/A')

                writer.writerow({
                    "Handle": product_data["titulo"].lower().replace(" ", "-"),
                    "Title": product_data["titulo"],
                    "Body (HTML)": product_data["Descrição do produto"],
                    # "Vendor": product_data["Fabricante"],
                    # "Product Category": "Saúde e beleza > Cuidados pessoais > Lubrificantes pessoais",
                    "Product Category": "Saúde e beleza > Cuidados pessoais",
                    "Product Type": "Biquíni",
                    "Tags": "Biquíni",
                    "Option1 Name": "Cor",
                    "Option1 Value": cor,
                    "Option2 Name": "Tamanho",
                    "Option2 Value": tamanho,
                    "Variant SKU": str(variation["SKU"]),
                    "Variant Price": variant_price,
                    "Compare At Price": "",
                    "Image Src": variation["Imagens da variação"],
                    "Published": "TRUE",
                    "Variant Inventory Tracker": "shopify",
                    "Variant Inventory Qty": inventory_qty,  # Ajustado com base na disponibilidade
                    "Variant Inventory Policy": "deny",
                    "Variant Fulfillment Service": "manual",
                    "Variant Requires Shipping": "TRUE",
                    "Variant Taxable": "TRUE",
                    "Gift Card": "FALSE",
                    "SEO Title": "",
                    "SEO Description": "",
                    "Status": "active",
                    "Collection": "Biquíni"
                })

# Exemplo de uso
convert_to_csv('produtosMiess.json', 'produtosMiess.csv')
