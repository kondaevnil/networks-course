from fastapi import FastAPI, File, HTTPException, UploadFile
import os

from fastapi.responses import FileResponse


class Product:
    def __init__(self, name, description, icon):
        self.name = name
        self.description = description
        self.icon = icon
    
    def to_json(self, id):
        return {
            "id": id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon
        }


class Store:
    def __init__(self):
        self.products = dict()
        self.product_id = 0
    
    def add_product(self, name, description, icon=""):
        self.product_id += 1
        product = Product(name, description, icon)
        self.products[self.product_id] = product
        return product.to_json(self.product_id)
    
    def get_product(self, id):
        return self.products.get(id).to_json(id) if self.products.get(id) else None
    
    def get_all_products(self):
        return (product.to_json(id) for id, product in self.products.items())
    
    def remove_product(self, id):
        return self.products.pop(id, None)
    
    def edit_product(self, id, name, description):
        product = self.products.get(id)
        if product:
            product.name = name
            product.description = description
        return product.to_json(id) if product else None


store = Store()

store.add_product("product1", "description1")
store.add_product("product2", "description2")
store.add_product("product3", "description3")

images_dir = "./images"

app = FastAPI()

@app.get("/products")
def get_products():
    return store.get_all_products()

@app.get("/product/{product_id}")
def get_product(product_id: int):
    return store.get_product(product_id)

@app.post("/product")
def add_product(name: str, description: str):
    return store.add_product(name, description)

@app.delete("/product/{product_id}")
def remove_product(product_id: int):
    return store.remove_product(product_id)

@app.put("/product/{product_id}")
def edit_product(product_id: int, name: str, description: str):
    return store.edit_product(product_id, name, description)

@app.post("/product/{product_id}/image")
async def upload_image(product_id: int, icon: UploadFile = File(...)):
    product = store.products.get(product_id)
    if product:
            file_extension = icon.filename.split(".")[-1]
            file_name = f"{product_id}.{file_extension}"
            file_path = os.path.join(images_dir, file_name)
            product.icon = file_path

            with open(file_path, "wb") as buffer:
                buffer.write(await icon.read())

            return {"message": "ok", "file_path": file_path}
    else:
        raise HTTPException(status_code=404, detail="Product not found")
    

@app.get("/product/{product_id}/image")
async def get_image(product_id: int):
    product = store.products.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for file_name in os.listdir(images_dir):
        if file_name.startswith(str(product_id) + "."):
            file_path = os.path.join(images_dir, file_name)
            return FileResponse(file_path)

    raise HTTPException(status_code=404, detail="Image not found")
