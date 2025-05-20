
verificarSelect2();

function verificarSelect2() {
    if ($('.select2').length > 0) {
        $('.select2').select2({
            width: '100%'
        });
    }
}

function verificarMascara() {
    $('.money').mask('000.000.000,00', { reverse: true });
}

document.getElementById("add-peca").addEventListener("click", function () {
    adicionarPeca();
});

document.querySelectorAll(".remove-peca").forEach(function (button) {
    button.addEventListener("click", function () {
        removerPeca(this);
    });
});

function adicionarPeca() {
    const template = document.querySelector("#pecas-empty-form");
    if (!template) {
        console.error("Template de peça não encontrado");
        return;
    }

    let newForm = template.content.querySelector('tr').cloneNode(true);
    const pecaForms = document.querySelectorAll(".pecas-form");
    let totalForms = document.getElementById("id_pecas_ordem_servico-TOTAL_FORMS");
    let formIndex = pecaForms.length;

    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formIndex);

    let formInputs = newForm.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.value = '';
    });

    totalForms.value = formIndex + 1;

    document.getElementById("pecas").appendChild(newForm);
    verificarSelect2();
    verificarMascara();
}

function removerPeca(button) {
    const pecaForms = document.querySelectorAll('.pecas-form');
    if (pecaForms.length <= 1) {
        alert("Deve haver pelo menos uma peça.");
        return;
    }
    const pecaForm = button.closest('.pecas-form');
    if (pecaForm) {
        pecaForm.remove();
        atualizarIndicesPecas();
    }
}

function atualizarIndicesPecas() {
    const pecaForms = document.querySelectorAll('.pecas-form');
    const totalForms = document.getElementById("id_pecas_ordem_servico-TOTAL_FORMS");
    totalForms.value = pecaForms.length;
    pecaForms.forEach((formRow, index) => {
        formRow.querySelectorAll('input, select').forEach(input => {
            const name = input.name;
            const newName = name.replace(/-\d+-/, `-${index}-`);
            const id = input.id;
            const newId = id.replace(/-\d+-/, `-${index}-`);
            input.name = newName;
            input.id = newId;
        });
    });
}

document.getElementById("add-pagamento").addEventListener("click", function () {
    adicionarPagamento();
});

document.querySelectorAll(".remove-pagamento").forEach(function (button) {
    button.addEventListener("click", function () {
        removerPagamento(this);
    });
});

function adicionarPagamento() {
    const template = document.querySelector("#pagamento-empty-form");
    if (!template) {
        console.error("Template de pagamento não encontrado");
        return;
    }

    let newForm = template.content.querySelector('tr').cloneNode(true);
    const pagamentoForms = document.querySelectorAll(".pagamento-form");
    let totalForms = document.getElementById("id_pagamentos-TOTAL_FORMS");
    let formIndex = pagamentoForms.length;

    newForm.innerHTML = newForm.innerHTML.replace(/__prefix__/g, formIndex);

    let formInputs = newForm.querySelectorAll('input, select');
    formInputs.forEach(input => {
        input.value = '';
    });

    totalForms.value = formIndex + 1;
    document.getElementById("pagamentos").appendChild(newForm);
    verificarSelect2();
    verificarMascara();
    // adicionar addEventListener para o novo campo de valor
    const valorInput = newForm.querySelector('input[name$=valor]');
    valorInput.addEventListener('input', calcularValorServico);
}

function removerPagamento(button) {
    const pagamentoForms = document.querySelectorAll('.pagamento-form');
    if (pagamentoForms.length <= 1) {
        alert("Deve haver pelo menos uma forma de pagamento.");
        return;
    }
    const pagamentoForm = button.closest('.pagamento-form');
    if (pagamentoForm) {
        pagamentoForm.remove();
        atualizarIndicesPagamentos();
    }
}

function atualizarIndicesPagamentos() {
    const pagamentoForms = document.querySelectorAll('.pagamento-form');
    const totalForms = document.getElementById("id_pagamentos-TOTAL_FORMS");
    totalForms.value = pagamentoForms.length;
    pagamentoForms.forEach((formRow, index) => {
        formRow.querySelectorAll('input, select').forEach(input => {
            const name = input.name;
            const newName = name.replace(/-\d+-/, `-${index}-`);
            const id = input.id;
            const newId = id.replace(/-\d+-/, `-${index}-`);
            input.name = newName;
            input.id = newId;
        });
    });
}