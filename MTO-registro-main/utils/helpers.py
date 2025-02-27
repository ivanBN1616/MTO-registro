def ajustar_texto(texto, ancho=40):
    import textwrap
    return "\n".join(textwrap.wrap(texto, width=ancho))
