    elif id_route == '%tabela%':
        if not params:
            resource = Todos%tabela%s
        else:
            resource = %tabela%PorId
        model = %tabela%Model()
