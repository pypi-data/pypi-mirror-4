def function(inputdic, inputgt, outputgt):
    if inputdic["input"].string == "": 
        return {}
    dni = inputdic["input"].string
    letras = 'TRWAGMYFPDXBNJZSQVHLCKE'
    resto = int(dni[:8]) % 23
    return {"output":letras[resto]}


iclass = "PythonTransformer"
inputdic = {"input":"DNINumber"}
outputdic = {"output":"DNIGrammar"}
