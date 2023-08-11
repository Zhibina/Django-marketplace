document.addEventListener("DOMContentLoaded", function() {

    const product_id = document.getElementById("load-more-btn").getAttribute("data-product-id");
    const container = document.getElementById("reviews-container");
    const loadMoreBtn = document.getElementById("load-more-btn");
    let offset = 0;
    const limit = 3;

    const formatDate = (dateString) => {
    const date = new Date(dateString);

    const months = [
      "ЯНВАРЬ",
      "ФЕВРАЛЬ",
      "МАРТ",
      "АПРЕЛЬ",
      "МАЙ",
      "ИЮНЬ",
      "ИЮЛЬ",
      "АВГУСТ",
      "СЕНТЯБРЬ",
      "ОКТЯБРЬ",
      "НОЯБРЬ",
      "ДЕКАБРЬ"
    ];

    const formattedDate = `${months[date.getMonth()]} ${date.getDate()} / ${date.getFullYear()} / ${date.getHours()}:${date.getMinutes()}`;

    return formattedDate;
    };

    const getUsername = (user) => {
    let user_name = "";
    if (user.firstname && user.lastname) {
    user_name = user.firstname + " " + user.lastname;
    } else {
    user_name = user.username;
    }
    return user_name;
    };

  const loadReviews = () => {
    fetch(`/products/api/reviews/?product_id=${product_id}&offset=${offset}&limit=${limit}`)
      .then(response => response.json())
      .then(reviews => {
        offset += limit;
        if (reviews.data.length === 0) {
          loadMoreBtn.style.display = "none";
        }
        reviews.data.forEach(review => {
          const name = getUsername(review.user);
          console.log("Username:", name);
          const formattedDate = formatDate(review.created);
          const html = `
            <header class="Section-header">
                <h3 class="Section-title"> ${review.number + offset - limit} отзыв
                </h3>
            </header>
            <div class="Comments">
                <div class="Comment">
                    <div class="Comment-column Comment-column_pict">
                        <div class="Comment-avatar">
                        <img src="${review.user.avatar}" alt="avatar">
                        </div>
                    </div>
                    <div class="Comment-column">
                        <header class="Comment-header">
                            <div>
                                <strong class="Comment-title">${name}
                                <div class="rating-result">
                                <span class="${review.rating >= 1 ? 'active' : ''}"></span>
                                <span class="${review.rating >= 2 ? 'active' : ''}"></span>
                                <span class="${review.rating >= 3 ? 'active' : ''}"></span>
                                <span class="${review.rating >= 4 ? 'active' : ''}"></span>
                                <span class="${review.rating >= 5 ? 'active' : ''}"></span>
                            </div>
                                </strong><span class="Comment-date">${formattedDate}</span>
                    </div>
                        </header>
                        <div class="Comment-content">
                            ${review.text}
                        </div>
                </div>
            </div>
          `
          ;
          container.insertAdjacentHTML("beforeend", html);
        });
      });
  };

  loadReviews();
  loadMoreBtn.addEventListener("click", loadReviews);
});
