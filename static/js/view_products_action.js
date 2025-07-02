document.addEventListener("DOMContentLoaded", function () {
    // Only run if on view products page
    if (!document.querySelector('.product-row')) return;

    rows.forEach(row => {
        row.addEventListener("contextmenu", function (event) {
            event.preventDefault();
            let menu = document.createElement("div");
            menu.className = "context-menu";

            if (viewDeleted) {
                menu.innerHTML = `<button onclick="editProduct(${row.dataset.id})">Edit</button>
                                  <button onclick="restoreProduct(${row.dataset.id})">Restore</button>`;
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

function editProduct(productId) {
    window.location.href = `/edit_product/${productId}`;
}

function deleteProduct(productId) {
    if (confirm("Are you sure you want to delete this product?")) {
        fetch(`/delete_product/${productId}`, { method: "POST" })
            .then(() => window.location.reload());
    }
}

function restoreProduct(productId) {
    fetch(`/restore_product/${productId}`, { method: "POST" })
        .then(() => window.location.reload());
}

function updateQuantity(productId, input) {
    let quantity = parseInt(input.value);
    if (isNaN(quantity) || quantity < 0) {
        quantity = 0;
    }
    input.value = quantity;

    fetch(`/update_quantity/${productId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ quantity: quantity })
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              input.style.backgroundColor = "#d4edda"; // Light green for success
              setTimeout(() => input.style.backgroundColor = "", 500);
          }
      });
}


const toggleDeleted = document.getElementById("toggleDeleted");
if (toggleDeleted) {
    toggleDeleted.addEventListener("change", function() {
        const viewDeleted = this.checked ? 1 : 0;
        window.location.href = `?view_deleted=${viewDeleted}`;
    });
}
