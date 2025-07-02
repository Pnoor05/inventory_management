// Set viewDeleted flag
const viewDeleted = JSON.parse('{{ view_deleted|tojson }}');

// Handle context menu
document.addEventListener("DOMContentLoaded", function () {
    const rows = document.querySelectorAll(".product-row");

    rows.forEach(row => {
        row.addEventListener("contextmenu", function (event) {
            event.preventDefault();
            let menu = document.createElement("div");
            menu.className = "context-menu";

            if (viewDeleted) {
                menu.innerHTML = `<button onclick="restoreProduct(${row.dataset.id})">Restore</button>`;
            } else {
                menu.innerHTML = `<button onclick="editProduct(${row.dataset.id})">Edit</button>
                                  <button onclick="deleteProduct(${row.dataset.id})">Delete</button>`;
            }

            document.body.appendChild(menu);
            menu.style.left = `${event.pageX}px`;
            menu.style.top = `${event.pageY}px`;

            document.addEventListener("click", () => menu.remove(), { once: true });
        });
    });
});

// Function to edit product
function editProduct(productId) {
    window.location.href = `/edit_product/${productId}`;
}

// Function to delete product
function deleteProduct(productId) {
    if (confirm("Are you sure you want to delete this product?")) {
        fetch(`/delete_product/${productId}`, { method: "POST" })
            .then(() => window.location.reload());
    }
}

// Function to restore product
function restoreProduct(productId) {
    fetch(`/restore_product/${productId}`, { method: "POST" })
        .then(() => window.location.reload());
}
