function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length == 2) return parts.pop().split(';').shift();
}

function saveChanges(postId) {
    const description = document.querySelector(`#textarea_${postId}`).value;
    const editedContent = document.getElementById(`${postId}_content`);
    const     modal = document.getElementById(`edit_post_${ postId }`);

    fetch(`/edit/${postId}`, {
        method: "POST",
        headers: {"Content-type": "application/json", "X-CSRFToken": getCookie("csrftoken")},
        body: JSON.stringify({
        "description": description,
        })  
    })
    .then(response => response.json())
    .then(result => {
      editedContent.innerHTML = result.data;

      modal.classList.remove("show");
      modal.setAttribute('aria-hidden', 'true');
      modal.style.display = 'none';

      // Remove the modal backdrop
      const backdrops = document.querySelectorAll('.modal-backdrop');
      backdrops.forEach(backdrop => backdrop.remove());

      // Reset the body's overflow and padding
      document.body.classList.remove('modal-open');
      document.body.style.paddingRight = '';

    })
}

function isLike(postId) {
    const button = document.getElementById(`likeButton_${postId}`);
    const likeCount = document.getElementById(`likeCount_${postId}`);

    fetch(`/like/${postId}`, {
        method: "PUT",
        headers: {
            'Content-Type': 'application/json',
            "X-CSRFToken": getCookie("csrftoken"),
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(result => {
        button.innerHTML = result.isLike;
        likeCount.innerHTML = result.likeCount;

    })
}