        document.addEventListener("input", function(e) {
            const target = e.target;

            // CPF
            if (target.name === "cpf") {
                let v = target.value.replace(/\D/g, "");
                if (v.length > 3) v = v.replace(/^(\d{3})(\d)/, "$1.$2");
                if (v.length > 7) v = v.replace(/^(\d{3})\.(\d{3})(\d)/, "$1.$2.$3");
                if (v.length > 11) v = v.replace(/^(\d{3})\.(\d{3})\.(\d{3})(\d)/, "$1.$2.$3-$4");
                target.value = v;
            }

            // CELULAR
            if (target.name === "telefone") {
                let v = target.value.replace(/\D/g, "");
                if (v.length > 0) v = v.replace(/^(\d{2})/, "($1) ");
                if (v.length > 6) v = v.replace(/\((\d{2})\)\s(\d{5})(\d)/, "($1) $2-$3");
                target.value = v;
            }
        });