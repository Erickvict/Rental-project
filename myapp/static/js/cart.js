async function updateQuantity(itemId, action) {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  const formData = new FormData();

  formData.append("action", action);
  formData.append("csrfmiddlewaretoken", csrfToken);

  try {
    const response = await fetch(`/cart/update/${itemId}/`, {
      method: "POST",

      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },

      body: formData,
    });

    const data = await response.json();

    if (!data.success) {
      showToast(data.message || "Something went wrong.", "error");

      return;
    }

    if (data.removed) {
      document.getElementById(`cart-item-${itemId}`).remove();

      showToast("Item removed from cart.", "success");
    } else {
      document.getElementById(`quantity-${itemId}`).textContent = data.quantity;

      document.getElementById(`subtotal-${itemId}`).textContent =
        `₹${data.subtotal}`;
    }

    updateCartBadge(data.cart_count);

    updateCartTotal(data.cart_total);
  } catch (error) {
    console.error(error);

    showToast("Something went wrong.", "error");
  }
}

async function removeFromCart(itemId) {
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

  const formData = new FormData();

  formData.append("csrfmiddlewaretoken", csrfToken);

  try {
    const response = await fetch(`/cart/remove/${itemId}/`, {
      method: "POST",

      headers: {
        "X-Requested-With": "XMLHttpRequest",
      },

      body: formData,
    });

    const data = await response.json();

    if (data.success) {
      const item = document.getElementById(`cart-item-${itemId}`);

      if (item) {
        item.remove();
      }

      updateCartBadge(data.cart_count);

      updateCartTotal(data.cart_total);

      showToast(data.message, "success");

      checkEmptyCart();
    }
  } catch (error) {
    console.error(error);

    showToast("Unable to remove item.", "error");
  }
}

function updateCartBadge(count) {
  const badge = document.getElementById("cart-badge");

  if (!badge) return;

  badge.textContent = count;

  badge.style.transform = "scale(1.3)";

  setTimeout(() => {
    badge.style.transform = "scale(1)";
  }, 300);
}

function updateCartTotal(total) {
  document.querySelectorAll(".cart-total").forEach((element) => {
    element.textContent = `₹${total}`;
  });
}

function checkEmptyCart() {
  const cartItems = document.querySelector(".cart-item");

  if (!cartItems) {
    location.reload();
  }
}

function showToast(message, type = "success") {
  const container =
    document.querySelector(".messages-container") || createToastContainer();

  const toast = document.createElement("div");

  const classes = type === "success" ? "bg-green-500" : "bg-red-500";

  toast.className = `
        ${classes}
        text-white
        px-5
        py-3
        rounded-lg
        shadow-lg
        flex
        items-center
        justify-between
        gap-4
        mb-3
        animate-pulse
    `;

  toast.innerHTML = `
        <span>${message}</span>

        <button
            onclick="this.parentElement.remove()"
            class="text-white text-xl font-bold"
        >
            ×
        </button>
    `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.remove();
  }, 4000);
}

function createToastContainer() {
  const div = document.createElement("div");

  div.className = `
        messages-container
        fixed
        top-5
        right-5
        z-50
        w-80
    `;

  document.body.appendChild(div);

  return div;
}



