document.addEventListener("DOMContentLoaded", function () {
    let cart = [];

    const searchInput = document.getElementById("posSearchInput");
    const productGrid = document.getElementById("posProductGrid");
    const cartItemsContainer = document.getElementById("cartItemsContainer");
    const emptyCartMsg = document.getElementById("emptyCartMessage");
    const subtotalEl = document.getElementById("cartSubtotal");
    const discountEl = document.getElementById("discountInput");
    const netTotalEl = document.getElementById("cartNetTotal");
    const checkoutBtn = document.getElementById("checkoutBtn");
    const clearCartBtn = document.getElementById("clearCartBtn");
    const customerSelect = document.getElementById("customerSelect");

    // 1. Search / Barcode Filter
    searchInput?.addEventListener("input", function () {
        const term = this.value.toLowerCase().trim();
        const items = document.querySelectorAll(".pos-product-item");

        items.forEach(item => {
            const name = item.dataset.name.toLowerCase();
            const barcode = item.dataset.barcode.toLowerCase();
            if (name.includes(term) || barcode.includes(term)) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    });

    // Handle Enter key for fast barcode scanners
    searchInput?.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            e.preventDefault();
            const term = this.value.toLowerCase().trim();
            const matched = Array.from(document.querySelectorAll(".pos-product-item"))
                .find(item => item.dataset.barcode.toLowerCase() === term || item.dataset.name.toLowerCase() === term);
            
            if (matched && parseInt(matched.dataset.stock) > 0) {
                addProductToCart(matched);
                this.value = "";
                // trigger input event to reset view
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });

    // 2. Click Product Card to Add
    productGrid?.addEventListener("click", function (e) {
        const itemCard = e.target.closest(".pos-product-item");
        if (!itemCard) return;

        const stock = parseInt(itemCard.dataset.stock);
        if (stock <= 0) {
            alert("This item is currently out of stock!");
            return;
        }

        addProductToCart(itemCard);
    });

    function addProductToCart(itemCard) {
        const id = parseInt(itemCard.dataset.id);
        const name = itemCard.dataset.name;
        const price = parseFloat(itemCard.dataset.price);
        const stock = parseInt(itemCard.dataset.stock);
        const unit = itemCard.dataset.unit;

        const existing = cart.find(c => c.id === id);
        if (existing) {
            if (existing.qty + 1 > stock) {
                alert(`Cannot add more than available stock (${stock} ${unit}).`);
                return;
            }
            existing.qty += 1;
        } else {
            cart.push({ id, name, price, stock, unit, qty: 1 });
        }

        renderCart();
    }

    // 3. Render Cart UI
    function renderCart() {
        if (cart.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="text-center py-4 text-muted" id="emptyCartMessage">
                    <i class="fa-solid fa-basket-shopping fa-2x text-muted mb-2"></i>
                    <p class="small mb-0">Cart is empty.<br>Scan or click products to add.</p>
                </div>
            `;
            subtotalEl.innerText = "₹0.00";
            netTotalEl.innerText = "₹0.00";
            checkoutBtn.disabled = true;
            return;
        }

        let subtotal = 0;
        let html = '<div class="list-group list-group-flush">';

        cart.forEach((item, index) => {
            const itemTotal = item.price * item.qty;
            subtotal += itemTotal;

            html += `
                <div class="list-group-item px-1 py-2 border-bottom">
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="text-truncate" style="max-width: 140px;">
                            <div class="fw-semibold small text-truncate">${item.name}</div>
                            <span class="text-muted fs-8">₹${item.price.toFixed(2)} / ${item.unit}</span>
                        </div>
                        <div class="d-flex align-items-center gap-1">
                            <button class="btn btn-sm btn-light border py-0 px-2 qty-btn" data-action="decrease" data-index="${index}">-</button>
                            <span class="fw-bold px-1 small">${item.qty}</span>
                            <button class="btn btn-sm btn-light border py-0 px-2 qty-btn" data-action="increase" data-index="${index}">+</button>
                        </div>
                        <div class="text-end">
                            <div class="fw-bold small">₹${itemTotal.toFixed(2)}</div>
                            <button class="btn btn-link text-danger p-0 fs-8 remove-btn" data-index="${index}">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        </div>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        cartItemsContainer.innerHTML = html;

        // Calculate Totals
        const discount = parseFloat(discountEl.value || 0);
        const net = Math.max(0, subtotal - discount);

        subtotalEl.innerText = `₹${subtotal.toFixed(2)}`;
        netTotalEl.innerText = `₹${net.toFixed(2)}`;
        checkoutBtn.disabled = false;
    }

    // 4. Cart Quantity & Remove Handlers
    cartItemsContainer?.addEventListener("click", function (e) {
        const qtyBtn = e.target.closest(".qty-btn");
        if (qtyBtn) {
            const index = parseInt(qtyBtn.dataset.index);
            const action = qtyBtn.dataset.action;
            const item = cart[index];

            if (action === "increase") {
                if (item.qty + 1 > item.stock) {
                    alert(`Maximum available stock reached (${item.stock} ${item.unit}).`);
                    return;
                }
                item.qty += 1;
            } else if (action === "decrease") {
                item.qty -= 1;
                if (item.qty <= 0) {
                    cart.splice(index, 1);
                }
            }
            renderCart();
            return;
        }

        const removeBtn = e.target.closest(".remove-btn");
        if (removeBtn) {
            const index = parseInt(removeBtn.dataset.index);
            cart.splice(index, 1);
            renderCart();
        }
    });

    discountEl?.addEventListener("input", renderCart);

    clearCartBtn?.addEventListener("click", function () {
        if (confirm("Are you sure you want to clear the active cart?")) {
            cart = [];
            renderCart();
        }
    });

    // 5. Checkout Action
    checkoutBtn?.addEventListener("click", function () {
        if (cart.length === 0) return;

        const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked').value;
        const customerId = customerSelect.value || null;
        const discount = parseFloat(discountEl.value || 0);

        if (paymentMethod === "CREDIT" && !customerId) {
            alert("⚠️ Please select a registered Khata Customer before completing an Udhar (Credit) sale!");
            customerSelect.focus();
            return;
        }

        const payload = {
            items: cart.map(i => ({ product_id: i.id, quantity: i.qty })),
            payment_method: paymentMethod,
            customer_id: customerId,
            discount_amount: discount
        };

        checkoutBtn.disabled = true;
        checkoutBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span> Processing...`;

        fetch("/billing/api/checkout/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Redirect directly to printable invoice
                window.location.href = `/billing/invoice/${data.invoice_number}/`;
            } else {
                alert("Checkout error: " + (data.error || "Unknown error"));
                checkoutBtn.disabled = false;
                checkoutBtn.innerHTML = `<i class="fa-solid fa-check-circle me-1"></i> Complete Sale & Bill`;
            }
        })
        .catch(err => {
            console.error("Checkout request failed:", err);
            alert("Network error processing transaction.");
            checkoutBtn.disabled = false;
            checkoutBtn.innerHTML = `<i class="fa-solid fa-check-circle me-1"></i> Complete Sale & Bill`;
        });
    });
});
