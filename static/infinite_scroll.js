let page = 1;
let loading = false;

// 載入文章
function loadPosts() {
    if (loading) return;
    loading = true;

    document.getElementById("loading").style.display = "block";

    fetch(`/api/posts?page=${page}`)
        .then(res => res.json())
        .then(data => {
            document.getElementById("loading").style.display = "none";

            const container = document.getElementById("post-container");

            data.posts.forEach(p => {
                const div = document.createElement("div");
                div.className = "post-card";

                div.innerHTML = `
                    <h2><a href="/posts/${p.id}">${p.title}</a></h2>
                    <p>作者：${p.author}｜${p.created_at}</p>
                    <span class="tag-badge">${p.tag}</span>   <!--顯示標籤 -->
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

// 第一次載入
loadPosts();

// 無限滾動觸發
window.addEventListener("scroll", () => {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 200) {
        loadPosts();
    }
});
