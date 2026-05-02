#Clase clientes Ronald Molina
class   Clientes:
    def __init__(self, nombre, email, telefono):
        #Enclapsulamiento de los datos "__"}
        self.__nombre = None
        self.__email=None
        self.__telefono = None
        
# uso de setter para validación
        self.__nombre(nombre)
        self.__email(email)
        self.__telefono(telefono)

#SETTER de validaciones para evitar errores en el ingreso de datos
    def set_nombre(self, nombre):
        if not nombre or len(nombre.strip())< 3:
            raise ValueError("El nombre ingresado debe tener al menos 3 caracteres en su longitud")
        self.__nombre = nombre.strip()
    
    def set_email(self, email):
        if not email or "@" not in email or "." not in email:
            raise ValueError("El email no es válido, seguramente no cuenta con @ o . ")
        