from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

def generate_views(modelo, form=None, paginacao=10, template_dir=''):
    """
    Gera as views baseadas no modelo e nos parâmetros fornecidos.
    
    :param modelo: Modelo do Django.
    :param form: Classe de formulário associada.
    :param paginacao: Número de itens por página na ListView.
    :param template_dir: Diretório onde os templates estão armazenados.
    :return: Dicionário contendo as views geradas.
    """

    class GeneratedListView(ListView):
        model = modelo
        template_name = f'{template_dir}/{modelo._meta.model_name}_list.html'
        paginate_by = paginacao
        context_object_name = 'items'

        def get_queryset(self):
            search = self.request.GET.get('search')
            if search:
                return modelo.objects.filter(nome__icontains=search)
            return modelo.objects.all()

    class GeneratedCreateView(CreateView):
        model = modelo
        form_class = form
        template_name = f'{template_dir}/{modelo._meta.model_name}_create.html'
        success_url = f'/{modelo._meta.model_name}'



        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs

    class GeneratedDetailView(DetailView):
        model = modelo
        template_name = f'{template_dir}/{modelo._meta.model_name}_detail.html'
        context_object_name = modelo._meta.model_name

        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            context['form'] = form(instance=self.object, disabled=True) if form else None
            return context

    class GeneratedUpdateView(UpdateView):
        model = modelo
        form_class = form
        template_name = f'{template_dir}/{modelo._meta.model_name}_edit.html'
        success_url = f'/{modelo._meta.model_name}'

        def get_form_kwargs(self):
            kwargs = super().get_form_kwargs()
            kwargs['user'] = self.request.user
            return kwargs

    class GeneratedDeleteView(DeleteView):
        model = modelo
        success_url = reverse_lazy(f'{modelo._meta.model_name}s:{modelo._meta.model_name}s')

    return {
        'list_view': GeneratedListView,
        'create_view': GeneratedCreateView,
        'detail_view': GeneratedDetailView,
        'update_view': GeneratedUpdateView,
        'delete_view': GeneratedDeleteView
    }
