$(function () {
  function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return "";
  }

  $(".js-add-cart").on("click", function () {
    var button = $(this);
    button.prop("disabled", true).text("Adding...");
    $.ajax({
      url: "/api/v1/cart/add/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        product_id: Number(button.data("product")),
        variant_id: button.data("variant") || null,
        quantity: Number($(".js-quantity").val() || 1)
      }),
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function () {
        button.text("Added");
      },
      error: function (xhr) {
        if (xhr.status === 403 || xhr.status === 401) {
          alert("Please log in before adding products to cart.");
        } else {
          alert("Could not add product to cart.");
        }
        button.prop("disabled", false).text("Add To Cart");
      }
    });
  });

  $(".js-add-wishlist").on("click", function () {
    var button = $(this);
    button.prop("disabled", true).text("Saving...");
    $.ajax({
      url: "/api/v1/wishlist/add/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ product_id: Number(button.data("product")), quantity: 1 }),
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function () {
        button.text("Wishlisted");
      },
      error: function (xhr) {
        if (xhr.status === 403 || xhr.status === 401) {
          alert("Please log in before using wishlist.");
        } else {
          alert("Could not update wishlist.");
        }
        button.prop("disabled", false).text("Wishlist");
      }
    });
  });

  $(".js-place-order").on("click", function () {
    var addressId = $("input[name='address_id']:checked").val();
    if (!addressId) {
      alert("Please select or add a delivery address.");
      return;
    }
    var button = $(this);
    button.prop("disabled", true).text("Placing...");
    $.ajax({
      url: "/api/v1/cart/place_order/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        address_id: Number(addressId),
        payment_method: $(".js-payment-method").val()
      }),
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function (response) {
        window.location.href = "/orders/" + response.data.id + "/";
      },
      error: function () {
        alert("Could not place order.");
        button.prop("disabled", false).text("Place Order");
      }
    });
  });

  $(".js-copy-link").on("click", function () {
    navigator.clipboard.writeText($(this).data("url"));
    $(this).text("Copied");
  });

  $(".js-submit-review").on("click", function () {
    var button = $(this);
    $.ajax({
      url: "/api/v1/reviews/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({
        product: Number(button.data("product")),
        rating: Number($(".js-review-rating").val()),
        title: $(".js-review-title").val(),
        body: $(".js-review-body").val()
      }),
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function () { button.text("Submitted"); },
      error: function () { alert("Could not submit review."); }
    });
  });

  $(".js-cancel-order").on("click", function () {
    var orderId = $(this).data("order");
    $.ajax({
      url: "/api/v1/orders/" + orderId + "/cancel/",
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify({ reason: "Customer requested cancellation" }),
      headers: { "X-CSRFToken": getCookie("csrftoken") },
      success: function () { window.location.reload(); },
      error: function () { alert("Could not request cancellation."); }
    });
  });
});
