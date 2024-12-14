    // Função para adicionar uma nova linha no formset
    document.getElementById('add-row').addEventListener('click', function() {
        var formset = document.getElementById('formset');
        var form_count = document.getElementById('id_form-TOTAL_FORMS').value;

        // Clonando o último formulário e incrementando o índice do formulário
        var new_form = formset.querySelector('.form-row').cloneNode(true);

        // Atualizando os índices dos campos do formulário para garantir que eles sejam únicos
        var regex = new RegExp('form-(\\d+)', 'g');
        new_form.innerHTML = new_form.innerHTML.replace(regex, 'form-' + form_count);

        // Limpando os valores do formulário
        var inputs = new_form.getElementsByTagName('input');
        for (var i = 0; i < inputs.length; i++) {
            inputs[i].value = '';
        }

        // Adicionando a nova linha ao formset
        formset.appendChild(new_form);

        // Atualizando o total de formulários
        document.getElementById('id_form-TOTAL_FORMS').value = parseInt(form_count) + 1;
    });

