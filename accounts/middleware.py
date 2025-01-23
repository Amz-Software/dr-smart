class LojaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se a loja foi salva na sessão
        request.loja_id = request.session.get('loja_id', None)
        # Processa a requisição
        response = self.get_response(request)
        
        return response
