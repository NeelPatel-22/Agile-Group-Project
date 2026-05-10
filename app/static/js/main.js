$(function () {
    const socket = typeof io !== "undefined" ? io() : null;

    function updateRecipeCardState(data) {
        const card = $(`.recipe-card[data-recipe-id="${data.id}"]`);
        if (!card.length) {
            return;
        }

        if (typeof data.comments_count !== "undefined") {
            card.find(".comment-counter").text(`${data.comments_count} comments`);
        }

        if (typeof data.likes_count !== "undefined") {
            card.find(".like-count").text(data.likes_count);
        }

        if (typeof data.liked !== "undefined") {
            card.find(".like-btn").toggleClass("active", data.liked);
        }

        if (typeof data.saved !== "undefined") {
            card.find(".save-btn").toggleClass("active", data.saved);
            card.find(".save-label").text(data.saved ? "Unsave Recipe" : "Save Recipe");
        }
    }

    function removeEmptyCommentState(list) {
        list.find(".comment-empty").remove();
    }

    function currentUserOwnsRecipe(card) {
        const currentUserId = $(".recipe-detail-main").data("current-user-id");
        return String(currentUserId) === String(card.data("recipe-owner-id"));
    }

    function normalizeCommentControls(card, commentItem) {
        const commentId = commentItem.data("comment-id");
        const existingButton = commentItem.children(".hide-comment-btn");

        if (currentUserOwnsRecipe(card)) {
            if (!existingButton.length) {
                commentItem.append(
                    `<button class="hide-comment-btn" type="button" data-comment-id="${commentId}">Hide</button>`
                );
            }
            return;
        }

        existingButton.remove();
    }

    function addCommentToCard(data) {
        const card = $(`.recipe-card[data-recipe-id="${data.recipe_id}"]`);
        if (!card.length) {
            return;
        }

        const list = card.find(".comment-list").first();
        removeEmptyCommentState(list);
        if (!list.find(`[data-comment-id="${data.comment_id}"]`).length) {
            list.prepend(data.comment_html);
        }
        normalizeCommentControls(card, list.find(`[data-comment-id="${data.comment_id}"]`).first());
        updateRecipeCardState({ id: data.recipe_id, comments_count: data.comments_count });
    }

    function hideCommentFromCard(data) {
        const commentItem = $(`.comment-item[data-comment-id="${data.comment_id}"]`);
        commentItem.slideUp(180, function () {
            const list = $(this).closest(".comment-list");
            $(this).remove();
            if (!list.find(".comment-item").length) {
                list.html('<p class="comment-empty mb-0">No comments yet.</p>');
            }
        });
        updateRecipeCardState({ id: data.recipe_id, comments_count: data.comments_count });
    }

    $(document).on("submit", ".comment-form", function (event) {
        event.preventDefault();

        const form = $(this);
        const recipeId = form.data("recipe-id");
        const input = form.find('input[name="content"]');
        const button = form.find('button[type="submit"]');

        button.prop("disabled", true);
        $.post(`/recipes/${recipeId}/comment`, form.serialize())
            .done(function (response) {
                addCommentToCard(response);
                input.val("");
            })
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not post comment.";
                alert(message);
            })
            .always(function () {
                button.prop("disabled", false);
            });
    });

    $(document).on("click", ".like-btn", function () {
        const button = $(this);
        const recipeId = button.data("recipe-id");

        button.prop("disabled", true);
        $.post(`/recipes/${recipeId}/like`)
            .done(updateRecipeCardState)
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not update like.";
                alert(message);
            })
            .always(function () {
                button.prop("disabled", false);
            });
    });

    $(document).on("click", ".save-btn", function () {
        const button = $(this);
        const recipeId = button.data("recipe-id");

        button.prop("disabled", true);
        $.post(`/recipes/${recipeId}/save`)
            .done(updateRecipeCardState)
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not update save.";
                alert(message);
            })
            .always(function () {
                button.prop("disabled", false);
            });
    });

    $(document).on("click", ".hide-comment-btn", function () {
        const button = $(this);
        const commentId = button.data("comment-id");

        button.prop("disabled", true);
        $.post(`/comments/${commentId}/hide`)
            .done(hideCommentFromCard)
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not hide comment.";
                alert(message);
                button.prop("disabled", false);
            });
    });

    if (socket) {
        socket.on("recipe_updated", updateRecipeCardState);
        socket.on("comment_added", addCommentToCard);
        socket.on("comment_hidden", hideCommentFromCard);
    }
});
