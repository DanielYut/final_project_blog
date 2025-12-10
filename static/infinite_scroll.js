let page = 1;
let loading = false;
let currentTag = ""; // ⭐ 目前篩選的分類

function loadPosts(reset = false) {
    if (loading) return;
    loading = true;

    document.getElementById("loading").style.display = "block";

    const tagParam = currentTag ? `&tag=${currentTag}` : "";

    fetch(`/api/posts?page=${page}${tagParam}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("loading").style.display = "none";

            if (reset) {
                document.getElementById("post-container").innerHTML = "";
            }

            const container = document.getElementById("post-container");

            data.posts.forEach(p => {
                const div = document.createElement("div");
                div.className = "post-card";

                const tagHTML = p.tag
                    ? `<span class="tag-badge tag-${p.tag}">${p.tag}</span>`
                    : "";

                div.innerHTML = `
                    <h2><a href="/posts/${p.id}" style="color:#5e35b1; text-decoration:none;">${p.title}</a></h2>
                    <p style="font-size:14px; color:gray;">作者：${p.author}｜${p.created_at}</p>
                    ${tagHTML}
                    <p>${p.content}</p>
                `;

                container.appendChild(div);
            });

            if (data.has_next) {
                page++;
                loading = false;
            }
        });
}


//  切換分類
function filterTag(tag, el) {
    currentTag = tag;
    page = 1;

    // 清空文章區
    document.getElementById("post-container").innerHTML = "";

    // 清除所有 tag 的 active 樣式
    document.querySelectorAll(".tag-item").forEach(btn => {
        btn.classList.remove("tag-active");
    });

    // 設定目前點擊的按鈕 active
    el.classList.add("tag-active");

    // 重新載入
    loadPosts(true);
}

//  首次載入
loadPosts();

//  無限捲動
window.addEventListener("scroll", () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 200) {
        loadPosts();
    }
});
