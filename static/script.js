let quizData = {};
let progressData = {};

let activeSection = "";
let activeTopic = "";

const $ = id => document.getElementById(id);

const sectionNames = {
    aptitude: "Aptitude",
    coding: "Coding",
    interview: "Interview"
};


// API FUNCTION

async function api(url, options = {}) {

    const response = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {})
        }
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}


// SHOW PAGES

function showView(id) {

    document.querySelectorAll(".view").forEach(view => {
        view.classList.add("hidden");
    });

    $(id).classList.remove("hidden");

    document.querySelectorAll(".nav-link").forEach(button => {

        button.classList.toggle(
            "active",
            button.dataset.view === id.replace("-view", "")
        );

    });
}


// STATUS BADGE

function badge(status) {

    return `
        <span class="status ${
            status === "Completed" ? "completed" : "pending"
        }">
            ${status}
        </span>
    `;
}


// LOAD DATA

async function loadAll() {

    [quizData, progressData] = await Promise.all([
        api("/api/quizzes"),
        api("/api/progress")
    ]);

    renderDashboard();
}


// DASHBOARD

function renderDashboard() {

    $("overall-percent").textContent =
        `${progressData.percentage}%`;

    $("overall-bar").style.width =
        `${progressData.percentage}%`;

    $("completed-count").textContent =
        `${progressData.completed} / ${progressData.total}`;

    $("pending-count").textContent =
        progressData.total - progressData.completed;


    $("dashboard-sections").innerHTML =
        Object.entries(quizData).map(([key, section]) => {

            const topics = Object.values(
                progressData.topics[key]
            );

            const done = topics.filter(
                topic => topic.status === "Completed"
            ).length;

            return `
                <article class="section-card">

                    <h3>${section.title}</h3>

                    <p>
                        ${done} of ${topics.length}
                        topics completed
                    </p>

                    <div class="progress-track">
                        <div class="progress-fill"
                             style="width:${
                                 topics.length
                                     ? done / topics.length * 100
                                     : 0
                             }%">
                        </div>
                    </div>

                    <button class="primary-btn"
                            onclick="openSection('${key}')">
                        View quizzes
                    </button>

                </article>
            `;

        }).join("");

    loadCompanies();
}


// OPEN SECTION

function openSection(section) {

    activeSection = section;

    $("section-title").textContent =
        sectionNames[section];

    $("topic-list").innerHTML =
        Object.entries(quizData[section].topics)
            .map(([topic, questions]) => {

                const p = progressData.topics[section][topic];

                return `
                    <article class="topic-card">

                        <h3>${topic}</h3>

                        <p>
                            ${questions.length} questions ·
                            ${p.attempts} attempts
                        </p>

                        <p>
                            Latest score: ${p.latest_score}%
                        </p>

                        ${badge(p.status)}

                        <button class="primary-btn"
                                onclick="startQuiz(
                                    '${section}',
                                    ${JSON.stringify(topic)}
                                )">
                            Start / Retake quiz
                        </button>

                    </article>
                `;

            }).join("");

    showView("quiz-list-view");
}


// START QUIZ

function startQuiz(section, topic) {

    activeSection = section;
    activeTopic = topic;

    const questions = quizData[section].topics[topic];

    $("quiz-section-label").textContent =
        sectionNames[section];

    $("quiz-topic-title").textContent = topic;

    $("question-count").textContent =
        `${questions.length} Questions`;

    $("quiz-result").classList.add("hidden");

    $("quiz-form").classList.remove("hidden");


    $("question-container").innerHTML =
        questions.map((q, i) => {

            return `
                <article class="question-card">

                    <h3>
                        ${i + 1}. ${q.question}
                    </h3>

                    ${q.options.map((option, j) => {

                        return `
                            <label class="option">

                                <input
                                    type="radio"
                                    name="question-${i}"
                                    value="${j}"
                                    required
                                >

                                <span>${option}</span>

                            </label>
                        `;

                    }).join("")}

                </article>
            `;

        }).join("");

    showView("quiz-view");
}


// SUBMIT QUIZ

$("quiz-form").addEventListener("submit", async event => {

    event.preventDefault();

    const questions =
        quizData[activeSection].topics[activeTopic];

    const answers = {};


    for (let i = 0; i < questions.length; i++) {

        const selected = document.querySelector(
            `input[name="question-${i}"]:checked`
        );

        if (!selected) {
            return alert("Please answer every question.");
        }

        answers[i] = Number(selected.value);
    }


    try {

        const result = await api("/api/submit-quiz", {

            method: "POST",

            body: JSON.stringify({
                section: activeSection,
                topic: activeTopic,
                answers: answers
            })

        });


        progressData = await api("/api/progress");

        renderDashboard();


        $("quiz-form").classList.add("hidden");

        const box = $("quiz-result");

        box.classList.remove("hidden");

        box.classList.toggle(
            "perfect",
            result.score === 100
        );


        box.innerHTML = `

            <h3>
                ${
                    result.score === 100
                        ? "🎉 Topic Completed!"
                        : "Keep Practicing!"
                }
            </h3>

            <p>
                <strong>
                    Your score: ${result.score}%
                    (${result.correct}/${result.total})
                </strong>
            </p>

            <p>
                Status: ${badge(result.status)}
            </p>

            <p>
                ${
                    result.score === 100
                        ? "Excellent! Every answer is correct."
                        : "You need 100% to mark this topic Completed. Review the explanations and try again."
                }
            </p>

            <h4>Answer Review</h4>

            ${result.review.map((r, i) => `

                <div class="review-item">

                    <strong>
                        ${i + 1}. ${r.question}
                    </strong>

                    <p class="${
                        r.is_correct
                            ? "correct-text"
                            : "wrong-text"
                    }">

                        ${r.is_correct ? "Correct" : "Incorrect"}

                    </p>

                    <small>${r.explanation}</small>

                </div>

            `).join("")}

            <button class="primary-btn"
                    onclick="startQuiz(
                        '${activeSection}',
                        ${JSON.stringify(activeTopic)}
                    )">
                Retake Quiz
            </button>

            <button class="text-btn"
                    onclick="openSection('${activeSection}')">
                Back to Topics
            </button>

        `;

    } catch (error) {

        alert(error.message);

    }

});


// NAVIGATION

document.querySelectorAll(".nav-link").forEach(button => {

    button.addEventListener("click", () => {

        const view = button.dataset.view;

        if (
            ["aptitude", "coding", "interview"].includes(view)
        ) {

            openSection(view);

        } else if (view === "companies") {

            showView("companies-view");

            loadCompanies();

        } else {

            showView("dashboard-view");

        }

    });

});


// BACK BUTTON

$("back-to-topics").addEventListener("click", () => {

    openSection(activeSection);

});


// ADD COMPANY

async function addCompany(nameId, roleId, statusId) {

    try {

        await api("/api/companies", {

            method: "POST",

            body: JSON.stringify({

                company: $(nameId).value,

                role: $(roleId).value,

                status: $(statusId).value

            })

        });

        $(nameId).value = "";
        $(roleId).value = "";

        loadCompanies();

    } catch (error) {

        alert(error.message);

    }

}


$("add-company").addEventListener("click", () => {

    addCompany(
        "company-name",
        "job-role",
        "company-status"
    );

});


$("add-company-page").addEventListener("click", () => {

    addCompany(
        "company-name-page",
        "job-role-page",
        "company-status-page"
    );

});


// LOAD COMPANIES

async function loadCompanies() {

    try {

        const companies = await api("/api/companies");

        const markup = companies.length

            ? companies.map(c => `

                <article class="company-item">

                    <div>

                        <strong>${escapeHtml(c.company)}</strong>

                        <small>
                            ${escapeHtml(c.role)} |
                            ${escapeHtml(c.status)}
                        </small>

                    </div>

                    <div class="company-actions">

                        <select
                            aria-label="Application status"
                            onchange="changeCompanyStatus(
                                ${c.id}, this.value
                            )"
                        >

                            ${[
                                "Applied",
                                "Assessment",
                                "Interview",
                                "Selected",
                                "Rejected"
                            ].map(s => `
                                <option ${
                                    s === c.status ? "selected" : ""
                                }>
                                    ${s}
                                </option>
                            `).join("")}

                        </select>

                        <button class="delete-btn"
                                onclick="removeCompany(${c.id})">
                            Delete
                        </button>

                    </div>

                </article>

            `).join("")

            : "<p>No company applications added yet.</p>";


        $("dashboard-companies").innerHTML = markup;

        $("companies-page-list").innerHTML = markup;

    } catch (error) {

        console.error(error);

    }

}


// UPDATE COMPANY STATUS

async function changeCompanyStatus(id, status) {

    try {

        await api(`/api/companies/${id}`, {

            method: "PUT",

            body: JSON.stringify({ status })

        });

        loadCompanies();

    } catch (error) {

        alert(error.message);

    }

}


// DELETE COMPANY

async function removeCompany(id) {

    if (!confirm("Delete this company application?")) {
        return;
    }

    await api(`/api/companies/${id}`, {
        method: "DELETE"
    });

    loadCompanies();

}


// HTML SAFETY

function escapeHtml(value) {

    return String(value).replace(/[&<>"']/g, c => ({

        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"

    }[c]));

}


// INITIALIZE

loadAll().catch(error => {

    console.error(error);

    alert(
        "Unable to load PrepPath. Check the Flask server and database."
    );

});