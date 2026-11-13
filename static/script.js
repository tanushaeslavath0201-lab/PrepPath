
// ---------------- NAVIGATION ----------------

function showPage(page) {
    document.querySelectorAll(".page").forEach(section => {
        section.classList.add("hidden");
    });

    document.getElementById(page).classList.remove("hidden");

    if (page === "dashboard") loadDashboard();
    if (page === "aptitude") loadTasks("Aptitude");
    if (page === "coding") loadTasks("Coding");
    if (page === "interview") loadTasks("Interview");
    if (page === "companies") loadCompanies();
}


// ---------------- DASHBOARD ----------------

async function loadDashboard() {
    const response = await fetch("/api/dashboard");
    const data = await response.json();

    document.getElementById("total").textContent = data.total;
    document.getElementById("completed").textContent = data.completed;
    document.getElementById("companiesCount").textContent = data.companies;
    document.getElementById("progress").textContent = data.progress + "%";

    document.getElementById("progressBar").style.width =
        data.progress + "%";

    document.getElementById("progressText").textContent =
        data.progress + "% Completed";

    document.getElementById("aptitudeCount").textContent = data.aptitude;
    document.getElementById("codingCount").textContent = data.coding;
    document.getElementById("interviewCount").textContent = data.interviews;
}


// ---------------- ADD TASK ----------------

async function addTask(category, inputId) {
    const input = document.getElementById(inputId);
    const title = input.value.trim();

    if (!title) {
        alert("Please enter a topic or problem");
        return;
    }

    let difficulty = "Medium";

    if (category === "Coding") {
        difficulty = document.getElementById("codingDifficulty").value;
    }

    const response = await fetch("/api/tasks", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            category: category,
            title: title,
            difficulty: difficulty
        })
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Unable to add task");
        return;
    }

    input.value = "";

    loadTasks(category);
    loadDashboard();
}


// ---------------- DISPLAY TASKS ----------------

async function loadTasks(category) {
    const response = await fetch(
        "/api/tasks?category=" + encodeURIComponent(category)
    );

    const tasks = await response.json();

    const listId = {
        "Aptitude": "aptitudeList",
        "Coding": "codingList",
        "Interview": "interviewList"
    }[category];

    const container = document.getElementById(listId);
    container.innerHTML = "";

    if (tasks.length === 0) {
        container.innerHTML = "<p>No tasks added yet.</p>";
        return;
    }

    tasks.forEach(task => {
        const div = document.createElement("div");
        div.className = "task";

        const info = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = task.title;

        const details = document.createElement("p");
        details.textContent =
            task.difficulty + " | " + task.status;

        info.append(title, details);

        const actions = document.createElement("div");

        const complete = document.createElement("button");
        complete.textContent =
            task.status === "Completed" ? "Undo" : "Complete";

        complete.onclick = () => updateTask(
            task.id,
            task.status === "Completed" ? "Pending" : "Completed",
            category
        );

        const remove = document.createElement("button");
        remove.textContent = "Delete";
        remove.className = "delete";
        remove.onclick = () => deleteTask(task.id, category);

        actions.append(complete, remove);
        div.append(info, actions);
        container.appendChild(div);
    });
}


// ---------------- UPDATE TASK ----------------

async function updateTask(id, status, category) {
    await fetch("/api/tasks/" + id, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({status: status})
    });

    loadTasks(category);
    loadDashboard();
}


// ---------------- DELETE TASK ----------------

async function deleteTask(id, category) {
    if (!confirm("Are you sure you want to delete this task?")) return;

    await fetch("/api/tasks/" + id, {
        method: "DELETE"
    });

    loadTasks(category);
    loadDashboard();
}


// ---------------- ADD COMPANY ----------------

async function addCompany() {
    const name = document.getElementById("companyName").value.trim();
    const role = document.getElementById("companyRole").value.trim();
    const status = document.getElementById("companyStatus").value;

    if (!name || !role) {
        alert("Enter company name and job role");
        return;
    }

    const response = await fetch("/api/companies", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({name, role, status})
    });

    const data = await response.json();

    if (!response.ok) {
        alert(data.error || "Unable to add company");
        return;
    }

    document.getElementById("companyName").value = "";
    document.getElementById("companyRole").value = "";

    loadCompanies();
    loadDashboard();
}


// ---------------- DISPLAY COMPANIES ----------------

async function loadCompanies() {
    const response = await fetch("/api/companies");
    const companies = await response.json();

    const container = document.getElementById("companyList");
    container.innerHTML = "";

    if (companies.length === 0) {
        container.innerHTML = "<p>No companies added yet.</p>";
        return;
    }

    companies.forEach(company => {
        const div = document.createElement("div");
        div.className = "task";

        const info = document.createElement("div");

        const title = document.createElement("strong");
        title.textContent = company.name;

        const details = document.createElement("p");
        details.textContent =
            company.role + " | " + company.status;

        info.append(title, details);

        const remove = document.createElement("button");
        remove.textContent = "Delete";
        remove.className = "delete";

        remove.onclick = async () => {
            if (!confirm("Delete this company?")) return;

            await fetch("/api/companies/" + company.id, {
                method: "DELETE"
            });

            loadCompanies();
            loadDashboard();
        };

        div.append(info, remove);
        container.appendChild(div);
    });
}


// ---------------- INITIAL LOAD ----------------

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
});
