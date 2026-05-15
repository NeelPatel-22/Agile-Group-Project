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

        if (type === "number" && value && !/^\d+$/.test(value)) {
            setFieldError(field, `${label} must be a number only.`);
            return false;
        }

        if (type === "number" && value && field.attr("min") && Number(value) < Number(field.attr("min"))) {
            setFieldError(field, `${label} must be at least ${field.attr("min")}.`);
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
            const label = data.comments_count === 1 ? "entry" : "entries";
            card.find(".comment-counter").text(`${data.comments_count} conversation ${label}`);
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
        const actionSlot = commentItem.children(".comment-owner-actions").first();
        const existingButton = actionSlot.find(".hide-comment-btn, .unhide-comment-btn");
        const isHidden = commentItem.data("comment-hidden") === true || commentItem.data("comment-hidden") === "true";

        if (currentUserOwnsRecipe(card)) {
            if (!existingButton.length) {
                const buttonClass = isHidden ? "unhide-comment-btn" : "hide-comment-btn";
                const buttonLabel = isHidden ? "Unhide" : "Hide";
                actionSlot.append(
                    `<button class="${buttonClass}" type="button" data-comment-id="${commentId}">${buttonLabel}</button>`
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

        if (card.find(`.comment-item[data-comment-id="${data.comment_id}"]`).length) {
            return;
        }

        const list = data.parent_id
            ? card.find(`.reply-list[data-parent-id="${data.parent_id}"]`).first()
            : card.find(".comment-list").first();

        if (!list.length) {
            return;
        }

        removeEmptyCommentState(card.find(".comment-list").first());
        const item = $(data.comment_html);
        list.prepend(item);
        normalizeCommentControls(card, item);
        updateRecipeCardState({ id: data.recipe_id, comments_count: data.comments_count });
    }

    function hideCommentFromCard(data) {
        const commentItem = $(`.comment-item[data-comment-id="${data.comment_id}"]`);
        const card = commentItem.closest(".recipe-card");
        if (card.length && currentUserOwnsRecipe(card)) {
            const replacement = $(data.comment_html);
            commentItem.replaceWith(replacement);
            normalizeCommentControls(card, replacement);
            updateRecipeCardState({ id: data.recipe_id, comments_count: data.comments_count });
            return;
        }

        commentItem.slideUp(180, function () {
            const list = $(this).closest(".comment-list");
            $(this).remove();
            if (!list.find(".comment-item").length) {
                list.html('<p class="comment-empty mb-0">No conversation yet.</p>');
            }
        });
        updateRecipeCardState({ id: data.recipe_id, comments_count: data.comments_count });
    }

    function unhideCommentOnCard(data) {
        const card = $(`.recipe-card[data-recipe-id="${data.recipe_id}"]`);
        if (!card.length) {
            return;
        }

        const rootList = card.find(".comment-list").first();
        const list = data.parent_id
            ? card.find(`.reply-list[data-parent-id="${data.parent_id}"]`).first()
            : rootList;
        const existing = card.find(`.comment-item[data-comment-id="${data.comment_id}"]`);
        if (existing.length) {
            const replacement = $(data.comment_html);
            existing.replaceWith(replacement);
            normalizeCommentControls(card, replacement);
        } else if (list.length) {
            removeEmptyCommentState(rootList);
            const item = $(data.comment_html);
            list.prepend(item);
            normalizeCommentControls(card, item);
        }
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

    function removeArchivedRecipeCard(data) {
        if (data.action !== "archived") {
            return;
        }

        const shouldRemoveFromPage = window.location.pathname === "/recipes" || /\/profile\/\d+$/.test(window.location.pathname);
        if (!shouldRemoveFromPage) {
            return;
        }

        const card = $(`.recipe-card[data-recipe-id="${data.id}"]`);
        card.slideUp(180, function () {
            $(this).remove();
        });
    }

    function removeUnarchivedRecipeCard(data) {
        if (!window.location.pathname.includes("/archived-recipes") || data.action !== "unarchived") {
            return;
        }

        const list = $(".archived-recipes-list");
        const card = list.find(`.recipe-card[data-recipe-id="${data.id}"]`);
        card.slideUp(180, function () {
            $(this).remove();
            const remainingCards = list.find(".recipe-card").length;

            if (remainingCards === 0 && !$(".archived-recipes-empty").length) {
                list.html(
                    '<div class="empty-profile-card archived-recipes-empty"><p class="mb-3">No archived recipes yet.</p><a href="/recipes" class="btn btn-primary">Explore Recipes</a></div>'
                );
            }
        });
    }

    function updateArchiveButton(button, data) {
        if (!button.length || typeof data.archived === "undefined") {
            return;
        }

        const nextAction = data.archived ? "unarchive" : "archive";
        const nextLabel = data.archived ? "Unarchive Recipe" : "Archive Recipe";
        button.data("archive-action", nextAction).attr("data-archive-action", nextAction);
        button.attr("aria-label", nextLabel).attr("title", nextLabel);
        button.find(".archive-label").text(nextLabel);
    }

    function updateProfileRecipeStats(data) {
        if (typeof data.active_recipes_count !== "undefined") {
            $('[data-stat="active-recipes-count"]').text(data.active_recipes_count);
        }

        if (typeof data.archived_recipes_count !== "undefined") {
            $('[data-stat="archived-recipes-count"]').text(data.archived_recipes_count);
        }

        if (typeof data.likes_received !== "undefined") {
            $('[data-stat="likes-received-count"]').text(data.likes_received);
        }
    }

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function activityIcon(type) {
        if (type === "comment") {
            return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4z"></path></svg>';
        }

        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M7 11v10H4a2 2 0 0 1-2-2v-6a2 2 0 0 1 2-2h3z"></path><path d="M7 11l4-8a3 3 0 0 1 3 3v5h4a2 2 0 0 1 2 2l-1 6a2 2 0 0 1-2 2H7"></path></svg>';
    }

    function activityCardHtml(activity) {
        const commentHtml = activity.comment_text
            ? `<p class="activity-comment">${escapeHtml(activity.comment_text)}</p>`
            : "";

        return `
            <article class="activity-card" data-activity-id="${escapeHtml(activity.id)}" data-activity-type="${escapeHtml(activity.type)}">
                <div class="activity-icon">${activityIcon(activity.type)}</div>
                <div class="activity-content">
                    <p class="activity-main">
                        <strong>${escapeHtml(activity.actor)}</strong>
                        ${escapeHtml(activity.action)}
                        <span class="activity-recipe">${escapeHtml(activity.recipe_title)}</span>
                    </p>
                    ${commentHtml}
                    <div class="activity-meta">
                        <span>${escapeHtml(activity.created_at_display)}</span>
                        <span>Recipe activity</span>
                    </div>
                </div>
            </article>
        `;
    }

    function updateActivityEmptyState() {
        const list = $("#activity-list");
        const count = list.find(".activity-card").length;
        $("#activity-count").text(count);
        $("#activity-empty").prop("hidden", count > 0);
    }

    function addActivityItem(activity, prepend) {
        const list = $("#activity-list");
        if (!list.length || !activity.id || list.find(`[data-activity-id="${activity.id}"]`).length) {
            return;
        }

        list.find(".activity-loading").remove();
        const item = $(activityCardHtml(activity));
        if (prepend) {
            list.prepend(item);
        } else {
            list.append(item);
        }
        updateActivityEmptyState();
    }

    function incrementActivityBadge() {
        const badge = $(".activity-nav-badge");
        if (!badge.length) {
            return;
        }

        const nextCount = Number(badge.text() || 0) + 1;
        badge.text(nextCount).prop("hidden", false);
    }

    function showActivityToast(activity) {
        $(".activity-toast").remove();
        const actionText = activity.type === "comment" ? "New conversation" : "New like";
        const toast = $(`
            <div class="activity-toast" role="status" aria-live="polite">
                <strong>${escapeHtml(actionText)}</strong>
                <span>${escapeHtml(activity.actor)} ${escapeHtml(activity.action)} ${escapeHtml(activity.recipe_title)}</span>
            </div>
        `);
        $("body").append(toast);

        window.setTimeout(function () {
            toast.addClass("show");
        }, 20);

        window.setTimeout(function () {
            toast.removeClass("show");
            window.setTimeout(function () {
                toast.remove();
            }, 240);
        }, 4200);
    }

    function loadActivityPage() {
        const page = $(".activity-page");
        if (!page.length) {
            return;
        }

        $(".activity-nav-badge").text(0).prop("hidden", true);

        $.getJSON(page.data("activity-endpoint"))
            .done(function (response) {
                const list = $("#activity-list");
                list.empty();
                (response.activities || []).forEach(function (activity) {
                    addActivityItem(activity, false);
                });
                updateActivityEmptyState();
            })
            .fail(function () {
                $("#activity-list").html('<div class="activity-loading">Could not load activity right now.</div>');
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
                const message = xhr.responseJSON?.message || "Could not update the conversation.";
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

    $(document).on("click", ".archive-btn", function () {
        const button = $(this);
        const recipeId = button.data("recipe-id");
        const action = button.data("archive-action") === "unarchive" ? "unarchive" : "archive";

        button.prop("disabled", true);
        $.post(`/recipes/${recipeId}/${action}`)
            .done(function (response) {
                updateArchiveButton(button, response);
                updateProfileRecipeStats(response);
                removeArchivedRecipeCard(response);
                removeUnarchivedRecipeCard(response);
            })
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not update archive status.";
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
                const message = xhr.responseJSON?.message || "Could not hide conversation entry.";
                alert(message);
                button.prop("disabled", false);
            });
    });

    $(document).on("click", ".reply-toggle-btn", function () {
        const form = $(this).closest(".comment-content").find(".reply-form").first();
        form.prop("hidden", !form.prop("hidden"));
        if (!form.prop("hidden")) {
            form.find('input[name="content"]').trigger("focus");
        }
    });

    $(document).on("submit", ".reply-form", function (event) {
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
                form.prop("hidden", true);
            })
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not add reply.";
                alert(message);
            })
            .always(function () {
                button.prop("disabled", false);
            });
    });

    $(document).on("click", ".unhide-comment-btn", function () {
        const button = $(this);
        const commentId = button.data("comment-id");

        button.prop("disabled", true);
        $.post(`/comments/${commentId}/unhide`)
            .done(unhideCommentOnCard)
            .fail(function (xhr) {
                const message = xhr.responseJSON?.message || "Could not unhide conversation entry.";
                alert(message);
                button.prop("disabled", false);
            });
    });

    if (socket) {
        socket.on("recipe_updated", updateRecipeCardState);
        socket.on("comment_added", addCommentToCard);
        socket.on("comment_hidden", hideCommentFromCard);
        socket.on("comment_unhidden", unhideCommentOnCard);
        socket.on("activity_added", function (activity) {
            addActivityItem(activity, true);
            incrementActivityBadge();
            showActivityToast(activity);
        });
        socket.on("owner_recipe_counts_updated", updateProfileRecipeStats);
    }

    loadActivityPage();
});
