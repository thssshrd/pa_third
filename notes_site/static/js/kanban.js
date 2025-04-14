// static/js/kanban.js

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".add-card-form").forEach(form => {
        form.addEventListener("submit", function (event) {
            event.preventDefault();  // Prevent default form submission

            let columnId = this.querySelector("[name='column_id']").value;
            let titleInput = this.querySelector("[name='title']");
            let title = titleInput.value.trim();
            let csrfToken = this.querySelector("[name='csrfmiddlewaretoken']").value;

            if (!title) {
                alert("Title cannot be empty!");
                return;
            }

            fetch(`/kanban/add_note/${columnId}/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": csrfToken
                },
                body: `title=${encodeURIComponent(title)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    titleInput.value = "";  // Clear input field

                    let column = document.querySelector(`[data-column-id="${data.column_id}"] .kanban-card-list`);
                    if (column) {
                        let newCard = document.createElement("div");
                        newCard.classList.add("kanban-card");
                        newCard.setAttribute("data-note-id", data.note_id);
                        newCard.setAttribute("draggable", "true");
                        newCard.innerHTML = `
                            <div class="kanban-card-title">${data.title}</div>
                        `;
                        column.appendChild(newCard);
                    }
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => console.error("Error:", error));
        });
    });
});

document.addEventListener("DOMContentLoaded", function () {
    let draggedCard = null;
    let originalColumn = null;

    // Enable dragging
    document.querySelectorAll(".kanban-card").forEach(card => {
        card.addEventListener("dragstart", function (event) {
            draggedCard = this;
            originalColumn = this.closest(".kanban-column").getAttribute("data-column-id");
            event.dataTransfer.effectAllowed = "move";
            setTimeout(() => this.classList.add("hidden"), 0); // Hide card while dragging
        });

        card.addEventListener("dragend", function () {
            this.classList.remove("hidden");
            draggedCard = null;
        });
    });

    // Enable dropping in a new position
    document.querySelectorAll(".kanban-card-list").forEach(list => {
        list.addEventListener("dragover", function (event) {
            event.preventDefault();
            const draggingCard = document.querySelector(".hidden");

            if (draggingCard) {
                const closest = [...this.children].find(child => {
                    return event.clientY <= child.getBoundingClientRect().top + child.offsetHeight / 2;
                });

                if (closest) {
                    this.insertBefore(draggingCard, closest);
                } else {
                    this.appendChild(draggingCard);
                }
            }
        });

        list.addEventListener("drop", function (event) {
            event.preventDefault();
            const draggingCard = document.querySelector(".hidden");

            if (draggingCard) {
                draggingCard.classList.remove("hidden");

                let newColumnId = this.closest(".kanban-column").getAttribute("data-column-id");
                let noteId = draggingCard.getAttribute("data-note-id");
                let newIndex = Array.from(this.children).indexOf(draggingCard);

                // Send update request to the backend
                fetch(`/kanban/update_note_position/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: JSON.stringify({
                        note_id: noteId,
                        column_id: newColumnId,
                        position: newIndex
                    })
                }).then(response => response.json())
                .then(data => {
                    if (data.status !== "success") {
                        alert("Failed to update card position");
                    }
                }).catch(error => console.error("Error:", error));
            }
        });
    });

    // Enable clicking to edit a card
    document.querySelectorAll(".kanban-card").forEach(card => {
        card.addEventListener("click", function (event) {
            if (!draggedCard) {
                let noteId = this.getAttribute("data-note-id");
                window.location.href = `/${noteId}/`;
            }
        });
    });
});