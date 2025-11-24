function formatCPF(value) {
    let v = value.replace(/\D/g, "");
    if (v.length > 3) v = v.replace(/^(\d{3})(\d)/, "$1.$2");
    if (v.length > 7) v = v.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
    if (v.length > 11) v = v.replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
    return v;
}

function formatPhone(value) {
    let v = value.replace(/\D/g, "");
    if (v.length > 0) v = v.replace(/^(\d{2})/, "($1) ");
    if (v.length > 6) v = v.replace(/\((\d{2})\)\s(\d{5})(\d)/, "($1) $2-$3");
    return v;
}

// Formata quando carrega a página
document.addEventListener("DOMContentLoaded", function () {
    const cpf = document.querySelector('input[name="cpf"]');
    const tel = document.querySelector('input[name="telefone"]');

    if (cpf && cpf.value) cpf.value = formatCPF(cpf.value);
    if (tel && tel.value) tel.value = formatPhone(tel.value);
});

// Mantém sua formatação ao digitar
document.addEventListener("input", function (e) {
    const target = e.target;

    if (target.name === "cpf") {
        target.value = formatCPF(target.value);
    }

    if (target.name === "telefone") {
        target.value = formatPhone(target.value);
    }
});