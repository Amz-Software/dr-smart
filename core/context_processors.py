


from urllib import request

from django.urls import reverse


def menu_items(request):
    items = [
        {
            "label": "Menu Principal",
            "url_name": "vendas:index",
            "icon": "bx bx-home-circle",
            "permission": "vendas.view_loja",
            "section": "Dr Smart",
        },
        {
            "label": "Produtos",
            "icon": "bx bx-mobile",
            "permission": "produtos.view_produto",
            "section": "Dr Smart",
            "sub_items": [
                {
                    "label": "Produtos",
                    "url_name": "produtos:produtos",
                    "permission": "produtos.view_produto",
                },
                {
                    "label": "Cor",
                    "url_name": "produtos:cores",
                    "permission": "produtos.view_produto",
                },
                {
                    "label": "Tipo",
                    "url_name": "produtos:tipos",
                    "permission": "produtos.view_produto",
                },
                {
                    "label": "Fabricante",
                    "url_name": "produtos:fabricantes",
                    "permission": "produtos.view_produto",
                },
                {
                    "label": "Estado",
                    "url_name": "produtos:estados",
                    "permission": "produtos.view_produto",
                },
                {
                    "label": "Memória",
                    "url_name": "produtos:memorias",
                    "permission": "produtos.view_produto",
                },
            ]
        },
        {          
            "label": "Caixa",
            "icon": "bx bx-cart",
            "permission": "vendas.view_caixa",
            "url_name": "vendas:caixa_list",
            "section": "Vendas"
        },
        {
            "label": "Estoque",
            "icon": "bx bx-box",
            "permission": "estoque.view_estoque",
            "sub_items": [
                {
                    "label": "Ver Estoque",
                    "url_name": "estoque:estoque_list",
                    "permission": "estoque.view_estoque"
                },
                {
                    "label": "Estoque IMEI",
                    "url_name": "estoque:estoque_imei_list",
                    "permission": "estoque.view_estoqueimei"  
                },
                {
                    "label": "Ver Entradas",
                    "url_name": "estoque:entrada_list",
                    "permission": "estoque.view_entradaestoque"
                },
                {
                    "label": "Adicionar Entrada",
                    "url_name": "estoque:estoque_entrada",
                    "permission": "estoque.add_entradaestoque"
                },
            ],
            "section": "Portal do Vendedor"
        },   
        {
            "label": "Vendas",
            "icon": "bx bx-box",
            "permission": "vendas.view_vendas",
            "section": "Vendas",
            "sub_items": [
                {
                    "label": "Iniciar Venda",
                    "url_name": "vendas:venda_list",
                    "permission": "vendas.view_venda"
                },
                {
                    "label": "Clientes",
                    "url_name": "vendas:cliente_list",
                    "permission": "vendas.view_cliente"
                },
                {
                    "label": "Tipo pagamento",
                    "url_name": "vendas:tipos_pagamento",
                    "permission": "vendas.view_tipopagamento"
                },
                {
                    "label": "Tipo venda",
                    "url_name": "vendas:tipos_venda",
                    "permission": "vendas.view_tipovenda"
                },
                {
                    "label": "Tipo entrega",
                    "url_name": "vendas:tipos_entrega",
                    "permission": "vendas.view_tipoentrega"
                },
            ],
        },
        {
            "label": "Financeiro",
            "icon": "bx bx-dollar-circle",
            "permission": "auth.view_user",
            "section": "Financeiro",
            "sub_items": [
                {
                    "label": "Caixa",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_user"
                },
                {
                    "label": "Caixa Total",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
                {
                    "label": "Relatótio de Vendas",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
                {
                    "label": "Contas a Receber",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
                {
                    "label": "Fechamentos Mensais",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
            ]
        },
        {
            "label": "Usuários",
            "icon": "bx bx-user",
            "permission": "auth.view_user",
            "section": "Configurações",
            "sub_items": [
                {
                    "label": "Usuários",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_user"
                },
                {
                    "label": "Grupos",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
                {
                    "label": "Permissões",
                    "url_name": "vendas:caixa_list",
                    "permission": "auth.view_group"
                },
            ]
        },
        {
            "label": "Configurações",
            "url_name": "vendas:caixa_list",
            "icon": "bx bx-cog",
            "permission": "auth.view_user",
            "section": "Configurações",
        },

        # {
        #     "label": "Exemplo",
        #     "icon": "bx bx-dollar-circle",
        #     "permission": "app.permission",
        #     "sub_items": [
        #         {
        #             "label": "",
        #             "url_name": "",
        #             "permission": ""
        #         },
        #         {
        #             "label": "",
        #             "url_name": "main:pre_sale_Form",
        #             "permission": "main.add_presale"
        #         },
        #         {
        #             "label": "",
        #             "url_name": "",
        #             "permission": ""
        #         }
        #     ],
        #     "section": "Portal do Vendedor"
        # },        

    ]
  

    current_path = request.path


    filtered_items = []
    sections = {}

    for item in items:
        item['active'] = False
        if 'sub_items' in item:
            visible_sub_items = []
            for sub_item in item['sub_items']:
                sub_item['url'] = reverse(sub_item['url_name'])
                if sub_item.get('permission') in request.user.get_all_permissions():
                    visible_sub_items.append(sub_item)
                    if sub_item['url'] == current_path:
                        item['active'] = True
                        sub_item['active'] = True
                    else:
                        sub_item['active'] = False
            item['sub_items'] = visible_sub_items
            if visible_sub_items:
                filtered_items.append(item)
        else:
            item['url'] = reverse(item['url_name']) if 'url_name' in item else None
            if item.get('permission') in request.user.get_all_permissions():
                filtered_items.append(item)
                if item['url'] == current_path:
                    item['active'] = True
            elif 'header' in item:
                filtered_items.append(item)


    for item in filtered_items:
        section = item['section']
        if section not in sections:
            sections[section] = []
        sections[section].append(item)


    return {'menu_items': sections}

