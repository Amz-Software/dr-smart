class LojaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print('Middleware chamado')
        # Verifica se a loja foi salva na sessão
        request.loja_id = request.session.get('loja_id', None)
        
        print('LOJA ID:', request.loja_id)
        # Processa a requisição
        response = self.get_response(request)
        
        return response
