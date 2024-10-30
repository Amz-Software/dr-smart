document.addEventListener("DOMContentLoaded", function() {
    const formTable = document.getElementById("produto-table").querySelector("tbody");
    const addButton = document.getElementById("add-product");
    const counterDisplay = document.getElementById("product-counter");
    
    let formCount = parseInt(document.getElementById("produto-table").dataset.formCount);
    const formsetPrefix = document.getElementById("produto-table").dataset.formsetPrefix;

    function checkSerializado(id_produto, imeiInput, quantityInput) {
        fetch(`/produto/details/${id_produto}/`)
            .then(response => response.json())
            .then(data => {
                if (data.serializado) {
                    console.log("Produto é serializado");
                    imeiInput.disabled = false;
                    quantityInput.value = 1;
                } else {
                    console.log("Produto não é serializado");
                    imeiInput.disabled = true;
                    imeiInput.value = '';
                }
            })
            .catch(error => {
                console.error("Erro ao verificar se o produto é serializado:", error);
            });
    }

    function updateCounter() {
        counterDisplay.textContent = `Produtos adicionados: ${formCount}`;
    }

    function addNewProductRow() {
        const lastForm = formTable.querySelector(".produto-form:last-child");
        if (lastForm) {
            const newForm = lastForm.cloneNode(true);
            newForm.querySelectorAll('input, select').forEach(function(element) {
                const name = element.name.replace(/-\d+-/, `-${formCount}-`);
                const id = element.id.replace(/-\d+-/, `-${formCount}-`);
                element.name = name;
                element.id = id;
                if (element.tagName === "SELECT") {
                    element.value = "";
                } else if (element.type === "checkbox") {
                    element.checked = false;
                    element.dispatchEvent(new Event('change'));
                } else {
                    if (!element.id.includes('quantidade')) {
                        element.value = "";
                    }
                }
            });

            const lastProdutoInput = lastForm.querySelector("select[id*='produto']");
            const lastCustoUnitarioInput = lastForm.querySelector("input[id*='custo_unitario']");
            const lastVendaUnitarioInput = lastForm.querySelector("input[id*='venda_unitaria']");
            const newQuantityInput = newForm.querySelector("input[id*='quantidade']");
            
            if (lastProdutoInput) {
                const selectedProdutoId = lastProdutoInput.value;
                newForm.querySelector("select[id*='produto']").value = selectedProdutoId;
                checkSerializado(selectedProdutoId, newForm.querySelector("input[id*='imei']"), newQuantityInput);
            }
            if (lastCustoUnitarioInput) {
                newForm.querySelector("input[id*='custo_unitario']").value = lastCustoUnitarioInput.value;
            }
            if (lastVendaUnitarioInput) {
                newForm.querySelector("input[id*='venda_unitaria']").value = lastVendaUnitarioInput.value;
            }

            formTable.appendChild(newForm);
            document.getElementById(`id_${formsetPrefix}-TOTAL_FORMS`).value = formCount + 1;
            formCount++;

            updateCounter();

            const imeiInput = newForm.querySelector("input[id*='imei']");
            imeiInput.focus();
        }
    }

    formTable.addEventListener("click", function(event) {
        if (event.target.classList.contains("remove-product")) {
            const row = event.target.closest(".produto-form");
            if (row) {
                row.remove();
                formCount--;
                document.getElementById(`id_${formsetPrefix}-TOTAL_FORMS`).value = formCount;
                updateCounter();
            }
        }
    });

    formTable.addEventListener("change", function(event) {
        const target = event.target;

        if (target.classList.contains("checkboxinput")) {
            const checkbox = target;
            const imeiInput = checkbox.closest("tr").querySelector("input[id*='imei']");
            const quantityInput = checkbox.closest("tr").querySelector("input[id*='quantidade']");
            toggleImeiInput(checkbox, imeiInput);
            checkSerializado(checkbox.closest("tr").querySelector("select[id*='produto']").value, imeiInput, quantityInput);
        }

        if (target.tagName === "SELECT") {
            const id_produto = target.value;
            const imeiInput = target.closest("tr").querySelector("input[id*='imei']");
            const quantityInput = target.closest("tr").querySelector("input[id*='quantidade']");
            checkSerializado(id_produto, imeiInput, quantityInput);
        }
    });

    formTable.addEventListener("keydown", function(event) {
        if (event.key === "Enter") {
            event.preventDefault();
            addNewProductRow();
        }
    });

    addButton.addEventListener("click", addNewProductRow);
});
