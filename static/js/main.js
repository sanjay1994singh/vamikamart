document.addEventListener("DOMContentLoaded", function () {
  function $(selector, root) {
    return (root || document).querySelector(selector);
  }

  function $$(selector, root) {
    return Array.prototype.slice.call((root || document).querySelectorAll(selector));
  }

  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  function requestJSON(url, options) {
    var settings = options || {};
    return fetch(url, {
      method: settings.method || "GET",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
        ...(settings.headers || {})
      },
      body: settings.body ? JSON.stringify(settings.body) : undefined,
      credentials: "same-origin"
    }).then(function (response) {
      return response.json().then(function (data) {
        if (!response.ok) {
          var error = new Error(data.message || "Request failed");
          error.status = response.status;
          throw error;
        }
        return data;
      });
    });
  }

  function cartQuantity(cart) {
    return (cart && cart.items ? cart.items : []).reduce(function (total, item) {
      return total + Number(item.quantity || 0);
    }, 0);
  }

  function cartTotal(cart) {
    return (cart && cart.items ? cart.items : []).reduce(function (total, item) {
      var price = item.product ? Number(item.product.selling_price || 0) : 0;
      return total + price * Number(item.quantity || 0);
    }, 0);
  }

  function cartProductMap(cart) {
    var map = {};
    (cart && cart.items ? cart.items : []).forEach(function (item) {
      if (item.product) map[item.product.id] = { itemId: item.id, quantity: Number(item.quantity || 0) };
    });
    return map;
  }

  function syncProductControls(cart) {
    var map = cartProductMap(cart);
    $$(".js-product-cart").forEach(function (control) {
      var state = map[Number(control.dataset.product)];
      var addButton = $(".js-add-cart", control);
      var qtyBox = $(".inline-qty", control);
      var qty = $(".js-card-qty", control);
      if (state && state.quantity > 0) {
        control.dataset.item = state.itemId;
        control.dataset.quantity = state.quantity;
        control.classList.add("in-cart");
        if (qty) qty.textContent = state.quantity;
        if (addButton) {
          addButton.disabled = false;
          addButton.hidden = true;
          addButton.classList.remove("is-loading", "is-added");
          addButton.textContent = "Add";
        }
        if (qtyBox) qtyBox.hidden = false;
      } else {
        delete control.dataset.item;
        control.dataset.quantity = "0";
        control.classList.remove("in-cart");
        if (qty) qty.textContent = "0";
        if (qtyBox) qtyBox.hidden = true;
        if (addButton) {
          addButton.disabled = false;
          addButton.hidden = false;
          addButton.classList.remove("is-loading", "is-added");
          addButton.textContent = "Add";
        }
      }
    });
  }

  function updateCartCount(cart) {
    var count = cartQuantity(cart);
    var itemLabel = $(".js-cart-items");
    var mobileItemLabel = $(".js-mobile-cart-items");
    var totalLabel = $(".js-cart-total");
    var cartButton = $(".cart-button");
    if (mobileItemLabel) mobileItemLabel.textContent = String(count);
    if (count > 0) {
      if (itemLabel) itemLabel.textContent = count + (count === 1 ? " item" : " items");
      if (totalLabel) {
        totalLabel.textContent = "₹" + Math.round(cartTotal(cart));
        totalLabel.hidden = false;
      }
      if (cartButton) cartButton.classList.add("has-items");
    } else {
      if (itemLabel) itemLabel.textContent = "My Cart";
      if (totalLabel) {
        totalLabel.textContent = "₹0";
        totalLabel.hidden = true;
      }
      if (cartButton) cartButton.classList.remove("has-items");
    }
    syncProductControls(cart);
  }

  var menuToggle = $(".mobile-menu-toggle");
  var mobileMenu = $(".mobile-menu-panel");
  if (menuToggle && mobileMenu) {
    menuToggle.addEventListener("click", function () {
      var isOpen = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", isOpen ? "false" : "true");
      mobileMenu.hidden = isOpen;
    });

    document.addEventListener("click", function (event) {
      if (mobileMenu.hidden) return;
      if (event.target.closest(".mobile-menu-toggle") || event.target.closest(".mobile-menu-panel")) return;
      menuToggle.setAttribute("aria-expanded", "false");
      mobileMenu.hidden = true;
    });

    window.addEventListener("resize", function () {
      if (window.innerWidth > 900) {
        menuToggle.setAttribute("aria-expanded", "false");
        mobileMenu.hidden = true;
      }
    });
  }

  var accountMenu = $(".account-menu");
  var accountToggle = $(".account-menu-toggle", accountMenu);
  var accountPanel = $(".account-menu-panel", accountMenu);
  function closeAccountMenu() {
    if (!accountToggle || !accountPanel) return;
    accountToggle.setAttribute("aria-expanded", "false");
    accountPanel.hidden = true;
  }
  if (accountToggle && accountPanel) {
    accountToggle.addEventListener("click", function () {
      var isOpen = accountToggle.getAttribute("aria-expanded") === "true";
      accountToggle.setAttribute("aria-expanded", isOpen ? "false" : "true");
      accountPanel.hidden = isOpen;
    });

    document.addEventListener("click", function (event) {
      if (accountPanel.hidden || event.target.closest(".account-menu")) return;
      closeAccountMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeAccountMenu();
    });
  }

  function refreshCartCount() {
    requestJSON("/api/v1/cart/current/").then(function (response) {
      updateCartCount(response.data);
    }).catch(function () {});
  }

  function showToast(message) {
    var stack = $(".toast-stack");
    if (!stack) return;
    var toast = document.createElement("div");
    toast.className = "store-toast";
    toast.textContent = message;
    stack.appendChild(toast);
    window.setTimeout(function () { toast.classList.add("is-visible"); }, 10);
    window.setTimeout(function () {
      toast.classList.remove("is-visible");
      window.setTimeout(function () { toast.remove(); }, 220);
    }, 1800);
  }

  $$(".js-use-location").forEach(function (button) {
    button.addEventListener("click", function () {
      if (!navigator.geolocation) {
        showToast("Location is not supported on this device.");
        return;
      }
      var form = button.closest("form");
      if (!form) return;
      button.disabled = true;
      button.textContent = "Detecting...";
      navigator.geolocation.getCurrentPosition(function (position) {
        var latitude = form.querySelector("input[name='latitude']");
        var longitude = form.querySelector("input[name='longitude']");
        if (latitude) latitude.value = position.coords.latitude.toFixed(6);
        if (longitude) longitude.value = position.coords.longitude.toFixed(6);
        button.disabled = false;
        button.textContent = "Use current location";
        showToast("Location added. Please complete house and locality.");
      }, function () {
        button.disabled = false;
        button.textContent = "Use current location";
        showToast("Location permission denied. Please type address manually.");
      }, { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 });
    });
  });

  function selectedPaymentMethod() {
    var checked = document.querySelector("input[name='payment_method']:checked");
    return checked ? checked.value : "cod";
  }

  function markPaymentMethod() {
    var method = selectedPaymentMethod();
    $$(".payment-option").forEach(function (option) {
      var input = option.querySelector("input[name='payment_method']");
      option.classList.toggle("is-selected", input && input.checked);
    });
    var note = $(".js-payment-note");
    if (note) {
      note.textContent = method === "razorpay"
        ? "Online payment selected. Razorpay will open after the order is created."
        : "COD selected. No online payment is collected now.";
    }
    var button = $(".js-place-order");
    if (button && !button.disabled) {
      button.textContent = method === "razorpay" ? "Pay Online" : "Place Order";
    }
  }

  function confirmRazorpayPayment(paymentId, razorpayResponse) {
    return requestJSON("/api/v1/payments/" + paymentId + "/confirm_razorpay/", {
      method: "POST",
      body: {
        razorpay_order_id: razorpayResponse.razorpay_order_id,
        razorpay_payment_id: razorpayResponse.razorpay_payment_id,
        razorpay_signature: razorpayResponse.razorpay_signature
      }
    });
  }

  function openRazorpayCheckout(orderData) {
    if (!window.Razorpay) {
      alert("Razorpay checkout could not be loaded. Please try again.");
      return;
    }
    if (!orderData.provider || orderData.provider.credentials_required) {
      alert("Razorpay is not configured yet. Please choose Cash On Delivery or add Razorpay keys in backend settings.");
      return;
    }
    var payment = orderData.payment || {};
    var provider = orderData.provider || {};
    var options = {
      key: provider.key_id,
      amount: provider.amount,
      currency: provider.currency || "INR",
      name: "VamikaMart",
      description: "Order " + orderData.order_number,
      order_id: provider.id,
      handler: function (razorpayResponse) {
        confirmRazorpayPayment(payment.id, razorpayResponse).then(function () {
          window.location.href = "/orders/" + orderData.id + "/";
        }).catch(function () {
          alert("Payment was received but verification failed. Please contact support with your payment ID.");
        });
      },
      modal: {
        ondismiss: function () {
          showToast("Online payment was cancelled. You can retry from payments.");
        }
      },
      theme: { color: "#1f6f5b" }
    };
    new window.Razorpay(options).open();
  }

  document.addEventListener("change", function (event) {
    if (event.target.matches("input[name='payment_method']")) {
      markPaymentMethod();
    }
  });

  document.addEventListener("click", function (event) {
    var addButton = event.target.closest(".js-add-cart");
    if (addButton) {
      addButton.disabled = true;
      addButton.classList.add("is-loading");
      addButton.textContent = "Adding";
      requestJSON("/api/v1/cart/add/", {
        method: "POST",
        body: {
          product_id: Number(addButton.dataset.product),
          variant_id: addButton.dataset.variant || null,
          quantity: Number(($(".js-quantity") || {}).value || 1)
        }
      }).then(function (response) {
        addButton.classList.remove("is-loading");
        addButton.classList.add("is-added");
        addButton.textContent = "Added";
        updateCartCount(response.data);
        showToast("Added to cart");
      }).catch(function (error) {
        alert(error.status === 401 || error.status === 403 ? "Please log in before adding products to cart." : "Could not add product to cart.");
        addButton.disabled = false;
        addButton.classList.remove("is-loading");
        addButton.textContent = "Add";
      });
      return;
    }

    var plusButton = event.target.closest(".js-card-plus");
    if (plusButton) {
      var plusControl = plusButton.closest(".js-product-cart");
      plusButton.disabled = true;
      requestJSON("/api/v1/cart/add/", {
        method: "POST",
        body: { product_id: Number(plusControl.dataset.product), variant_id: null, quantity: 1 }
      }).then(function (response) {
        updateCartCount(response.data);
      }).catch(function () {
        alert("Could not increase quantity.");
      }).finally(function () {
        plusButton.disabled = false;
      });
      return;
    }

    var minusButton = event.target.closest(".js-card-minus");
    if (minusButton) {
      var minusControl = minusButton.closest(".js-product-cart");
      var itemId = Number(minusControl.dataset.item);
      var quantity = Number(minusControl.dataset.quantity || 0);
      if (!itemId || quantity <= 0) return;
      minusButton.disabled = true;
      var request = quantity <= 1
        ? requestJSON("/api/v1/cart/remove/", { method: "POST", body: { item_id: itemId } })
        : requestJSON("/api/v1/cart/update_quantity/", { method: "POST", body: { item_id: itemId, quantity: quantity - 1 } });
      request.then(function (response) {
        updateCartCount(response.data);
      }).catch(function () {
        alert(quantity <= 1 ? "Could not remove product." : "Could not decrease quantity.");
      }).finally(function () {
        minusButton.disabled = false;
      });
      return;
    }

    var wishlistButton = event.target.closest(".js-add-wishlist");
    if (wishlistButton) {
      wishlistButton.disabled = true;
      wishlistButton.textContent = "Saving...";
      requestJSON("/api/v1/wishlist/add/", {
        method: "POST",
        body: { product_id: Number(wishlistButton.dataset.product), quantity: 1 }
      }).then(function () {
        wishlistButton.textContent = "Wishlisted";
      }).catch(function (error) {
        alert(error.status === 401 || error.status === 403 ? "Please log in before using wishlist." : "Could not update wishlist.");
        wishlistButton.disabled = false;
        wishlistButton.textContent = "Wishlist";
      });
      return;
    }

    var placeOrderButton = event.target.closest(".js-place-order");
    if (placeOrderButton) {
      var checkedAddress = document.querySelector("input[name='address_id']:checked");
      if (!checkedAddress) {
        alert("Please select or add a delivery address.");
        return;
      }
      var method = selectedPaymentMethod();
      placeOrderButton.disabled = true;
      placeOrderButton.textContent = method === "razorpay" ? "Opening payment..." : "Placing...";
      requestJSON("/api/v1/cart/place_order/", {
        method: "POST",
        headers: { "Idempotency-Key": "web-" + Date.now() },
        body: {
          address_id: Number(checkedAddress.value),
          payment_method: method
        }
      }).then(function (response) {
        if (method === "razorpay") {
          openRazorpayCheckout(response.data);
          placeOrderButton.disabled = false;
          markPaymentMethod();
        } else {
          window.location.href = "/orders/" + response.data.id + "/";
        }
      }).catch(function () {
        alert("Could not place order.");
        placeOrderButton.disabled = false;
        markPaymentMethod();
      });
      return;
    }

    var copyButton = event.target.closest(".js-copy-link");
    if (copyButton) {
      navigator.clipboard.writeText(copyButton.dataset.url || "");
      copyButton.textContent = "Copied";
      return;
    }

    var reviewButton = event.target.closest(".js-submit-review");
    if (reviewButton) {
      requestJSON("/api/v1/reviews/", {
        method: "POST",
        body: {
          product: Number(reviewButton.dataset.product),
          rating: Number(($(".js-review-rating") || {}).value),
          title: ($(".js-review-title") || {}).value,
          body: ($(".js-review-body") || {}).value
        }
      }).then(function () {
        reviewButton.textContent = "Submitted";
      }).catch(function () {
        alert("Could not submit review.");
      });
      return;
    }

    var cancelButton = event.target.closest(".js-cancel-order");
    if (cancelButton) {
      var reason = window.prompt("Cancellation reason", "Customer requested cancellation");
      if (reason === null) return;
      cancelButton.disabled = true;
      cancelButton.textContent = "Cancelling...";
      requestJSON("/api/v1/orders/" + cancelButton.dataset.order + "/cancel/", {
        method: "POST",
        body: { reason: reason || "Customer requested cancellation" }
      }).then(function () {
        window.location.reload();
      }).catch(function () {
        alert("Could not cancel order.");
        cancelButton.disabled = false;
        cancelButton.textContent = "Cancel Order";
      });
      return;
    }

    var cartQtyButton = event.target.closest(".js-cart-qty");
    if (cartQtyButton) {
      var newQuantity = Number(cartQtyButton.dataset.quantity);
      if (newQuantity < 1) return;
      cartQtyButton.disabled = true;
      requestJSON("/api/v1/cart/update_quantity/", {
        method: "POST",
        body: { item_id: Number(cartQtyButton.dataset.item), quantity: newQuantity }
      }).then(function () {
        window.location.reload();
      }).catch(function () {
        alert("Could not update cart quantity.");
        cartQtyButton.disabled = false;
      });
      return;
    }

    var removeButton = event.target.closest(".js-cart-remove");
    if (removeButton) {
      removeButton.disabled = true;
      removeButton.textContent = "Removing...";
      requestJSON("/api/v1/cart/remove/", {
        method: "POST",
        body: { item_id: Number(removeButton.dataset.item) }
      }).then(function () {
        window.location.reload();
      }).catch(function () {
        alert("Could not remove item.");
        removeButton.disabled = false;
        removeButton.textContent = "Remove";
      });
    }
  });

  refreshCartCount();
  markPaymentMethod();
  $$('input[type="password"]').forEach(function (input) {
    if (input.dataset.passwordToggleReady === "1") return;
    input.dataset.passwordToggleReady = "1";
    var wrapper = document.createElement("span");
    wrapper.className = "password-field-wrap";
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    var button = document.createElement("button");
    button.type = "button";
    button.className = "password-toggle";
    button.setAttribute("aria-label", "Show password");
    button.textContent = "👁";
    button.addEventListener("click", function () {
      var show = input.type === "password";
      input.type = show ? "text" : "password";
      button.setAttribute("aria-label", show ? "Hide password" : "Show password");
      button.classList.toggle("is-visible", show);
    });
    wrapper.appendChild(button);
  });
});
