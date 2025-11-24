function updateQuantity(itemId, change) {
    const qtyElement = document.getElementById('qty-' + itemId);
    let currentQty = parseInt(qtyElement.textContent);
    const newQty = Math.max(1, currentQty + change);
    
    if (newQty !== currentQty) {
        // Faz a requisição AJAX para atualizar no servidor
        fetch("{% url 'atualizar_quantidade' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: JSON.stringify({
                'produto_id': itemId,
                'quantidade': newQty
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Atualiza a quantidade visualmente
                qtyElement.textContent = newQty;
                // Atualiza o total do item
                document.getElementById('total-' + itemId).textContent = data.item_total;
                // Atualiza os totais do carrinho
                document.getElementById('subtotal').textContent = data.cart_total;
                document.getElementById('total-final').textContent = data.cart_total;
                
                // Se foi removido (quantidade = 0), recarrega
                if (data.removed) {
                    setTimeout(() => {
                        window.location.reload();
                    }, 500);
                }
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            window.location.reload();
        });
    }
}