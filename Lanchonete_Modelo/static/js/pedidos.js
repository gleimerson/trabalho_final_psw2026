"use strict";

const adicionar = document.getElementById("adicionar-item");
const total = document.getElementById("id_itens-TOTAL_FORMS");
const maximo = document.getElementById("id_itens-MAX_NUM_FORMS");
const modelo = document.getElementById("item-vazio");
const itens = document.getElementById("itens");

if (adicionar && total && maximo && modelo && itens) {
    const atualizar = () => { adicionar.disabled = Number(total.value) >= Number(maximo.value); };
    atualizar();
    adicionar.addEventListener("click", () => {
        const indice = Number(total.value);
        if (indice >= Number(maximo.value)) return;
        itens.insertAdjacentHTML("beforeend", modelo.innerHTML.replaceAll("__prefix__", String(indice)));
        total.value = String(indice + 1);
        atualizar();
        itens.lastElementChild.querySelector("select")?.focus();
    });
}
