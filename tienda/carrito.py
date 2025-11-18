class Carrito:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        carrito = self.session.get("carrito")
        if not carrito:
            carrito = self.session["carrito"] = {}
        self.carrito = carrito

    def agregar(self, libro):
        if str(libro.id) not in self.carrito:
            self.carrito[str(libro.id)] = {
                "producto_id": libro.id,
                "nombre": libro.titulo,
                "precio": float(libro.precio),
                "imagen": libro.portada.url,
                "acumulado": float(libro.precio)
            }
        self.guardar()

    def guardar(self):
        self.session["carrito"] = self.carrito
        self.session.modified = True

    def eliminar(self, libro):
        id = str(libro.id)
        if id in self.carrito:
            del self.carrito[id]
            self.guardar()

    def limpiar(self):
        self.session["carrito"] = {}
        self.session.modified = True
        
    
    
    def obtener_subtotal(self):
        total = 0
        for key, value in self.carrito.items():
            total += float(value["acumulado"])
        return total

    def obtener_iva(self):
        
        return round(self.obtener_subtotal() * 0.16, 2)

    def obtener_total_con_iva(self):
        
        return round(self.obtener_subtotal() + self.obtener_iva(), 2)
    
    
    def obtener_total_precio(self):
        return self.obtener_subtotal()