# import json

# data = {}

# for i in range(1, 10001):
#     key = f"row_key_{i}"
#     data[key] = {
#         "info_personal": {
#             "nombre": f"valor_nuevo_{(i-1)*4+1}",
#             "edad": f"valor_nuevo_{(i-1)*4+2}",
#         },
#         "contacto": {
#             "telefono": f"valor_nuevo_{(i-1)*4+3}",
#             "email": f"valor_nuevo_{(i-1)*4+4}",
#         },
#     }

# with open("output.json", "w") as outfile:
#     json.dump(data, outfile, indent=4)


import json

data = {}

for i in range(1, 10001):
    key = f"row_key_{i}"
    data[key] = {
        "info_personal": {
            "nombre": f"valor_nuevo_{(10000-i)*4+1}",
            "edad": f"valor_nuevo_{(10000-i)*4+2}",
        },
        "contacto": {
            "telefono": f"valor_nuevo_{(10000-i)*4+3}",
            "email": f"valor_nuevo_{(10000-i)*4+4}",
        },
    }

with open("data_update.json", "w") as outfile:
    json.dump(data, outfile, indent=4)
