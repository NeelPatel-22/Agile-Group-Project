$(function () {
    const socket = typeof io !== "undefined" ? io() : null;
    const allowedImageExtensions = ["png", "jpg", "jpeg", "gif", "webp"];

    function smartTrim(value) {
        return value.replace(/\s+/g, " ").trim();
    }

    function normalizeField(input) {
        const field = $(input);
        const type = (field.attr("type") || "").toLowerCase();
        const tag = input.tagName.toLowerCase();

        if (type === "file" || type === "password") {
            return;
        }

        if (tag === "textarea") {
            field.val(field.val().replace(/[ \t]+\n/g, "\n").trim());
            return;
        }

        const normalized = smartTrim(field.val());
        field.val(type === "email" ? normalized.toLowerCase() : normalized);

        if (field.data("format") === "cook-time" && /^\d+$/.test(field.val())) {
            field.val(`${field.val()} minutes`);
        }

        if (field.data("format") === "servings" && /^\d+$/.test(field.val())) {
            field.val(`${field.val()} servings`);
        }
    }

    function setFieldError(field, message) {
        const wrapper = field.closest(".mb-3, .recipe-filter-group, .meta-grid > div, .full-span, .input-group").first();
        field.addClass("is-invalid").removeClass("is-valid");
        wrapper.find(".field-error").remove();
        if (message) {
            wrapper.append(`<span class="field-error">${message}</span>`);
        }
    }

    function clearFieldError(field) {
        const wrapper = field.closest(".mb-3, .recipe-filter-group, .meta-grid > div, .full-span, .input-group").first();
        field.removeClass("is-invalid");
        wrapper.find(".field-error").remove();
        if (field.val() && field.prop("required")) {
            field.addClass("is-valid");
        }
    }

    function validateField(input) {
        const field = $(input);
        const label = field.data("label") || field.closest("div").find("label").first().text() || "This field";
        const value = field.val();
        const minLength = Number(field.attr("minlength") || 0);
        const type = (field.attr("type") || "").toLowerCase();
        const matchName = field.data("match-field");

        if (field.prop("required") && !value) {
            setFieldError(field, `${label} is required.`);
            return false;
        }

        if (type === "email" && value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
            setFieldError(field, "Enter a valid email address.");
            return false;
        }

        if (minLength && value && value.length < minLength) {
            setFieldError(field, `${label} must be at least ${minLength} characters.`);
            return false;
        }

        if (type === "file" && value) {
            const extension = value.split(".").pop().toLowerCase();
            const allowed = (field.data("allowed-extensions") || allowedImageExtensions.join(",")).split(",");
            if (!allowed.includes(extension)) {
                setFieldError(field, `Upload one of: ${allowed.join(", ")}.`);
                return false;
            }
        }

        if (matchName) {
            const other = field.closest("form").find(`[name="${matchName}"]`);
            if (other.length && value !== other.val()) {
                setFieldError(field, "Passwords do not match.");
                return false;
            }
        }

        clearFieldError(field);
        return true;
    }

    $(document).on("blur", "input, textarea", function () {
        normalizeField(this);
        if ($(this).closest("form").hasClass("needs-smart-validation")) {
            validateField(this);
        }
    });

    $(document).on("submit", "form.needs-smart-validation", function (event) {
        const form = $(this);
        let isValid = true;

        form.find("input, textarea, select").each(function () {
            normalizeField(this);
            if (!validateField(this)) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            form.find(".is-invalid").first().trigger("focus");
        }
    });

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

    function removeUnsavedRecipeCard(data) {
        if (!window.location.pathname.includes("/saved-recipes") || data.action !== "removed") {
            return;
        }

        const list = $(".saved-recipes-list");
        const card = list.find(`.recipe-card[data-recipe-id="${data.id}"]`);
        card.slideUp(180, function () {
            $(this).remove();
            const remainingCards = list.find(".recipe-card").length;
            $(".saved-recipes-total").text(remainingCards);

            if (remainingCards === 0 && !$(".saved-recipes-empty").length) {
                list.html(
                    '<div class="empty-profile-card saved-recipes-empty"><p class="mb-3">You have not saved any recipes yet.</p><a href="/recipes" class="btn btn-primary">Explore Recipes</a></div>'
                );
            }
        });
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
            .done(function (response) {
                updateRecipeCardState(response);
                removeUnsavedRecipeCard(response);
            })
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
