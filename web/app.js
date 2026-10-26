"use strict";
const $ = (selector) => document.querySelector(selector);
const state = {
  data: null,
  session: localStorage.getItem("home-agent-session") || "demo",
  busy: false,
  approval: null,
  engineInitialized: false,
};
const titles = {
  assistant: [
    "A little less to think about.",
    "Everyday tasks, a well-stocked kitchen, and something good to cook.",
  ],
  kitchen: [
    "Good food starts here.",
    "Know what you have. Make something you’ll love.",
  ],
  activity: [
    "The little things, taken care of.",
    "Review every action and follow the changes in your household.",
  ],
  connections: [
    "A home for your connections.",
    "See which services are available and choose your AI model.",
  ],
};
const prompts = {
  en: {
    train: "Check train 12627 tomorrow",
    bill: "Pay electricity bill DEMO-1042",
    recipe: "Cook tomato rice for 2 with less chilli",
    suggest: "Suggest something to cook",
  },
  ta: {
    train: "ரயில் 12627 நாளை நிலை",
    bill: "மின் கட்டணம் DEMO-1042",
    recipe: "தக்காளி சாதம் சமைக்க வேண்டும், காரம் குறை",
    suggest: "இன்று என்ன சமைக்கலாம்?",
  },
  ml: {
    train: "ട്രെയിൻ 12627 നാളെ നില",
    bill: "വൈദ്യുതി ബിൽ DEMO-1042",
    recipe: "തക്കാളി ചോറ് പാചകം ചെയ്യാം, എരിവ് കുറയ്ക്കണം",
    suggest: "ഭക്ഷണ നിർദേശങ്ങൾ തരൂ",
  },
  kn: {
    train: "ರೈಲು 12627 ನಾಳೆ ಸ್ಥಿತಿ",
    bill: "ವಿದ್ಯುತ್ ಬಿಲ್ DEMO-1042",
    recipe: "ಟೊಮೆಟೊ ಅನ್ನ ಅಡುಗೆ ಮಾಡೋಣ, ಖಾರ ಕಡಿಮೆ",
    suggest: "ಊಟಕ್ಕೆ ಸಲಹೆ ನೀಡಿ",
  },
  hi: {
    train: "ट्रेन 12627 की स्थिति 2026-11-01",
    bill: "बिजली बिल DEMO-1042",
    recipe: "टमाटर चावल बनाना है, कम तीखा",
    suggest: "खाने का सुझाव दें",
  },
};
const taskNames = {
  train_status: "Train status",
  bill_preview: "Electricity bill",
  booking_preview: "Journey booking",
  recipe_plan: "Cooking plan",
  dish_suggestions: "Dinner ideas",
  inventory_list: "Kitchen stock",
};
const statusNames = {
  awaiting_approval: "Needs approval",
  needs_input: "Needs details",
  succeeded: "Completed",
  failed: "Unavailable",
  cancelled: "Cancelled",
  planned: "Ready to cook",
};
function el(tag, className, value) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (value !== undefined) node.textContent = String(value);
  return node;
}
function toast(message, error = false) {
  const node = $("#toast");
  node.textContent = message;
  node.className = error ? "error" : "";
  node.hidden = false;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => {
    node.hidden = true;
  }, 7000);
}
async function api(path, body) {
  const options =
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Home-Agent": "local-console",
          },
          body: JSON.stringify(body),
        };
  const response = await fetch(path, options);
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error("The server returned an invalid response. Please retry.");
  }
  if (!response.ok)
    throw new Error(
      data.error?.message || "The request could not be completed.",
    );
  return data;
}
async function run(action, button) {
  if (button) button.disabled = true;
  try {
    return await action();
  } catch (error) {
    toast(error.message, true);
    return null;
  } finally {
    if (button) button.disabled = false;
  }
}
function setView(name) {
  if (!titles[name]) return;
  document
    .querySelectorAll(".view")
    .forEach((node) =>
      node.classList.toggle("active", node.id === "view-" + name),
    );
  document.querySelectorAll(".nav-item").forEach((node) => {
    const active = node.dataset.view === name;
    node.classList.toggle("active", active);
    if (active) node.setAttribute("aria-current", "page");
    else node.removeAttribute("aria-current");
  });
  $("#breadcrumb").textContent = name[0].toUpperCase() + name.slice(1);
  $("#page-title").textContent = titles[name][0];
  $("#page-description").textContent = titles[name][1];
  $("#new-chat").hidden = name !== "assistant";
}
async function refresh() {
  state.data = await api(
    "/api/state?session=" + encodeURIComponent(state.session),
  );
  renderAll();
}
function renderAll() {
  renderChat();
  renderInventory();
  renderActivity();
  renderConnections();
  const pending = state.data.tasks.filter(
    (task) => task.status === "awaiting_approval",
  );
  $("#inventory-count").textContent = state.data.inventory.length;
  $("#approval-count").textContent = pending.length;
  $("#pending-count").textContent = pending.length;
  $("#payment-count").textContent = state.data.metrics.sandbox_payments;
  const attention = $("#attention-list");
  attention.replaceChildren();
  if (!pending.length)
    attention.append(
      el(
        "p",
        "empty-note",
        "You’re all caught up. New sandbox actions will appear here for your review.",
      ),
    );
  else
    pending
      .slice(0, 3)
      .forEach((task) => attention.append(taskCard(task, true)));
}
function renderChat() {
  const log = $("#chat-log");
  log.replaceChildren();
  const messages = state.data.messages;
  if (!messages.length) {
    const welcome = el("div", "welcome");
    welcome.append(
      el("div", "welcome-mark", "h."),
      el("h3", "", "Make yourself at home."),
      el(
        "p",
        "",
        "Ask about a train, take care of a demo bill, or find something to cook. Choose your language and try a conversation below.",
      ),
    );
    log.append(welcome);
  }
  for (const message of messages) {
    appendMessage(log, "user", message.user_text, message.language);
    const response = message.response;
    const currentTask = response.task
      ? state.data.tasks.find((task) => task.id === response.task.id) || response.task
      : null;
    const displayReply = currentTask && currentTask.status !== response.task.status
      ? currentTask.result.summary
      : response.reply;
    const wrap = appendMessage(
      log,
      "assistant",
      displayReply,
      response.language,
    );
    const meta = el(
      "div",
      "message-meta",
      response.mode === "offline"
        ? "Offline template"
        : response.mode === "openrouter"
          ? `${response.model} · ${response.verified_actions || 0} verified tool results`
          : "Muse · tool-backed results are labeled",
    );
    if (state.data.integrations.tts) {
      const listen = el("button", "listen-button", "Listen ↗");
      listen.type = "button";
      listen.addEventListener("click", () =>
        playSpeech(displayReply, response.language, listen),
      );
      meta.append(listen);
    }
    wrap.append(meta);
    if (response.mode === "openrouter") {
      const evidence = el("details", "task-detail");
      evidence.append(el("summary", "", "Agent actions & limits"));
      evidence.append(el("p", "small-muted", response.notice));
      const trace = el("ol");
      (response.trace || []).forEach((step) => trace.append(el("li", "", `${taskNames[step.tool] || step.tool} · ${statusNames[step.status] || step.status}`)));
      if (!trace.childElementCount) evidence.append(el("p", "small-muted", "Conversation only. No tool action was executed."));
      else evidence.append(trace);
      wrap.append(evidence);
    }
    if (response.task) {
      wrap.append(taskCard(currentTask));
    }
  }
  $("#starters").hidden = messages.length > 0;
  log.scrollTop = log.scrollHeight;
}
function appendMessage(log, role, content, language) {
  const row = el("div", "message " + role);
  if (role !== "user") row.append(el("span", "message-avatar", "h."));
  const wrap = el("div", "bubble-wrap");
  const bubble = el("div", "bubble", content);
  bubble.lang = language;
  wrap.append(bubble);
  row.append(wrap);
  log.append(row);
  return wrap;
}
function taskCard(task, compact = false) {
  const card = el("article", "task-card" + (compact ? " pending-card" : ""));
  const head = el("div", "task-head");
  head.append(
    el("span", "task-title", taskNames[task.kind] || task.kind),
    el(
      "span",
      "task-badge " + task.status,
      statusNames[task.status] || task.status,
    ),
  );
  card.append(head);
  const result = task.result;
  if (result.mode)
    card.append(
      el(
        "p",
        "small-muted",
        {
          sandbox: "LOCAL SANDBOX · No real transaction",
          fixture: "SAMPLE DATA · Not live",
          curated: "CURATED RECIPE · English steps",
          inventory: "LOCAL HOUSEHOLD DATA",
        }[result.mode] || result.mode,
      ),
    );
  if (compact) card.append(el("p", "task-summary", result.summary));
  if (!compact && task.kind === "train_status") {
    card.append(el("p", "task-summary", result.summary));
  }
  if (!compact && task.kind === "bill_preview")
    card.append(
      el(
        "p",
        "task-summary",
        result.biller +
          " · " +
          result.account +
          " · ₹" +
          (result.amount_paise / 100).toFixed(2),
      ),
    );
  if (!compact && task.kind === "booking_preview")
    card.append(
      el(
        "p",
        "task-summary",
        `${result.origin} → ${result.destination} · ${result.date} · ₹${(result.amount_paise / 100).toFixed(2)}`,
      ),
    );
  if (!compact && task.kind === "recipe_plan") {
    if (Array.isArray(result.ingredients)) renderRecipe(card, task);
    else card.append(el("p", "task-summary", result.summary));
  }
  if (!compact && task.kind === "dish_suggestions")
    renderSuggestions(card, result.options);
  if (!compact && task.kind === "inventory_list")
    card.append(
      el(
        "p",
        "task-summary",
        result.items
          .map((item) => `${item.name}: ${item.quantity} ${item.unit}`)
          .join(" · "),
      ),
    );
  if (result.receipt)
    card.append(
      el("p", "inline-notice", "Sandbox reference: " + result.receipt),
    );
  const actions = el("div", "task-actions");
  if (task.status === "awaiting_approval") {
    const approve = el("button", "button primary", "Review & approve");
    approve.type = "button";
    approve.dataset.action = "review";
    approve.dataset.task = task.id;
    const cancel = el("button", "button secondary", "Cancel");
    cancel.type = "button";
    cancel.dataset.action = "cancel";
    cancel.dataset.task = task.id;
    actions.append(approve, cancel);
  }
  if (task.status === "planned") {
    const cooked = el("button", "button primary", "Mark cooked · update stock");
    cooked.type = "button";
    cooked.dataset.action = "complete";
    cooked.dataset.task = task.id;
    actions.append(cooked);
  }
  if (actions.childElementCount) card.append(actions);
  if (!compact) {
    const details = el("details", "task-detail");
    details.append(
      el("summary", "", "View source & task details"),
      el(
        "pre",
        "",
        JSON.stringify(
          { id: task.id, status: task.status, ...result },
          null,
          2,
        ),
      ),
    );
    card.append(details);
  }
  return card;
}
function renderRecipe(card, task) {
  const result = task.result;
  card.append(el("h3", "", `${result.name} · ${result.servings} servings`));
  const chips = el("div", "recipe-ingredients");
  result.ingredients.forEach((item) => {
    const chip = el(
      "span",
      "ingredient-chip" + (item.missing ? " missing" : ""),
      `${item.name} ${item.quantity} ${item.unit}${item.missing ? ` · need ${item.missing} more` : ""}`,
    );
    chips.append(chip);
  });
  card.append(chips);
  if (result.ingredients.some((item) => item.missing > 0))
    card.append(
      el(
        "p",
        "inline-notice",
        "Some ingredients are missing. Add groceries or correct stock before marking this meal cooked.",
      ),
    );
  const steps = el("ol", "recipe-steps");
  steps.lang = "en";
  result.steps.forEach((step) => steps.append(el("li", "", step)));
  card.append(steps);
}
function renderSuggestions(card, options) {
  for (const option of options) {
    const row = el("div", "suggestion-row");
    const copy = el("div");
    copy.append(
      el("strong", "", option.name),
      el(
        "p",
        "",
        `${option.time_minutes} min · ${option.missing.length ? "Missing: " + option.missing.map((item) => item.name).join(", ") : "All ingredients available"}${option.recently_cooked ? " · Recently cooked" : ""}`,
      ),
    );
    const button = el("button", "button secondary", "Plan ↗");
    button.type = "button";
    button.dataset.action = "plan";
    button.dataset.recipe = option.id;
    row.append(copy, button);
    card.append(row);
  }
}
function renderInventory() {
  const body = $("#inventory-body");
  body.replaceChildren();
  state.data.inventory.forEach((item) => {
    const row = el("tr");
    const low = item.quantity < { g: 100, ml: 50, pcs: 2 }[item.unit];
    row.append(
      el("td", "item-name", item.name),
      el("td", "", `${item.quantity} ${item.unit}`),
      el(
        "td",
        low ? "stock-low" : "",
        item.quantity === 0 ? "Out of stock" : low ? "Running low" : "In stock",
      ),
    );
    const cell = el("td");
    const edit = el("button", "table-action", "Correct");
    edit.type = "button";
    edit.setAttribute("aria-label", "Correct " + item.name + " stock");
    edit.dataset.action = "stock";
    edit.dataset.item = item.name;
    cell.append(edit);
    row.append(cell);
    body.append(row);
  });
}
function renderActivity() {
  const history = $("#task-history");
  history.replaceChildren();
  if (!state.data.tasks.length)
    history.append(
      el(
        "p",
        "empty-note",
        "Your first task will appear here. Try a train lookup or a sandbox bill.",
      ),
    );
  else state.data.tasks.forEach((task) => history.append(taskCard(task)));
  const events = $("#event-history");
  events.replaceChildren();
  state.data.events.forEach((event) => {
    const row = el("div", "event-row");
    row.append(
      el("strong", "item-name", event.name),
      el("small", "", event.source + (event.estimated ? " · Estimated" : "")),
      el(
        "span",
        "",
        `${event.delta > 0 ? "+" : ""}${event.delta} ${event.unit}`,
      ),
    );
    events.append(row);
  });
}
function renderConnections() {
  const data = state.data.integrations;
  const models = Array.isArray(data.models) ? data.models : [];
  const catalog = data.model_catalog;
  const list = $("#connections-list");
  list.replaceChildren();
  const rows = [
    [
      "Free AI · OpenRouter",
      "Live reasoning, tool calls and tool observations. Only free models are allowed; availability and quotas vary.",
      data.openrouter ? `${models.length} permitted free models` : "Not configured",
      data.openrouter && models.length > 0,
    ],
    [
      "Meta Muse",
      data.hosted ? "Separate Meta adapter available; this website currently uses OpenRouter." : data.model + " · direct API adapter",
      data.muse ? "Key configured · unverified" : "Needs API key",
      data.muse,
    ],
    [
      "Agent runtime",
      data.hosted ? "Bounded tool/observation loop is active. Hermes MCP integration remains available for a later connection." : "MCP tool server included. Connect using the documented configuration.",
      data.hosted ? "Application loop active" : "Adapter ready · not connected",
      false,
    ],
    [
      "WhatsApp",
      "Use Hermes’s gateway after choosing and testing your WhatsApp route.",
      "Not connected",
      false,
    ],
    [
      "Indic speech → text",
      "Configurable JSON adapter for your hosted Indic transcription service.",
      data.asr ? "Endpoint configured · unverified" : "Not connected",
      data.asr,
    ],
    [
      "Indic text → speech",
      "Configurable JSON adapter for your hosted Indic synthesis service.",
      data.tts ? "Endpoint configured · unverified" : "Not connected",
      data.tts,
    ],
    [
      "Travel & payments",
      "Train examples and transaction simulators; no real money moves and no tickets are issued.",
      "Fixtures & sandbox",
      false,
    ],
    [
      "Kitchen memory",
      data.hosted ? "Private per-visitor state saves purchases, corrections and meal estimates on the server. This browser's cookie grants access; workspaces are separate." : "SQLite stores purchases, corrections and estimated meal consumption.",
      data.hosted ? "Server storage active" : "Local storage active",
      true,
    ],
    [
      "Video & bill image extraction",
      "Use curated recipes and reviewed grocery text until media extraction is connected.",
      "Not connected",
      false,
    ],
  ];
  for (const [name, description, status, ready] of rows) {
    const row = el("div", "connection-row"),
      copy = el("div");
    copy.append(el("h3", "", name), el("p", "", description));
    row.append(
      copy,
      el("span", "connection-status" + (ready ? " ready" : ""), status),
    );
    list.append(row);
  }
  $("#engine").querySelector('[value="muse"]').disabled = !data.muse;
  $("#engine").querySelector('[value="openrouter"]').disabled = !data.openrouter;
  const select = $("#model-select");
  const previousModel = select.value;
  select.replaceChildren();
  for (const identifier of models) {
    const option = el("option", "", catalog?.names?.[identifier] || identifier);
    option.value = identifier;
    select.append(option);
  }
  if (!models.length) {
    const placeholder = el("option", "", "No verified free models available");
    placeholder.value = "";
    select.append(placeholder);
  }
  select.value = models.includes(previousModel) ? previousModel : (data.model || "");
  $("#model-access-note").textContent = catalog?.message
    ? `${catalog.message} Access settings refresh within one minute; reload after saving changes.`
    : "Free AI is not configured for this application.";
  if (!state.engineInitialized) {
    $("#engine").value = data.openrouter ? "openrouter" : "offline";
    state.engineInitialized = true;
  }
  select.disabled = $("#engine").value !== "openrouter" || !models.length;
  $("#runtime-label").textContent = data.hosted ? "Live Python app" : "Local prototype";
  $("#workspace-description").textContent = data.hosted ? "Your private demo workspace" : "Local demo workspace";
  $("#storage-label").textContent = data.hosted ? "Saved privately on the server" : "Saved on this computer";
  $("#connections-description").textContent = data.hosted
    ? "Choose your free AI model below. Kitchen data and task records are saved in your private browser workspace on the server."
    : "The local application works independently. Services below require their own configuration and validation.";
  $("#engine-hint").textContent = data.hosted
    ? "Free AI uses real model inference and tools. Offline mode uses a limited phrase matcher. Free provider capacity and account permissions can vary."
    : "The direct Muse adapter tests the same tool contracts. Hermes uses the separate MCP adapter; selecting Muse here does not run Hermes.";
  $("#speech-note").textContent = data.asr
    ? "Indic endpoint configured"
    : "Speech service not connected";
  $("#mode-title").textContent = $("#engine").value === "openrouter" ? (models.length ? "Free AI configured" : "Free AI needs model access") :
    $("#engine").value === "muse" ? "Muse selected" : "Offline demo";
  $("#mode-description").textContent =
    $("#engine").value === "openrouter"
      ? (models.length ? "Key-permitted models only · Provider capacity varies · Sandbox travel & payments" : catalog?.message || "No permitted free model is available.")
      : $("#engine").value === "muse"
      ? "Direct Meta API adapter · Sample train data · Sandbox transactions"
      : "Limited phrase matching · Sample train data · Sandbox transactions";
}
async function sendMessage(value) {
  if (state.busy) return;
  state.busy = true;
  $("#send-message").disabled = true;
  $("#conversation-mode").textContent = "Working on your request…";
  try {
    await api("/api/messages", {
      text: value,
      language: $("#language").value,
      session: state.session,
      request_id: crypto.randomUUID(),
      engine: $("#engine").value,
      model: $("#model-select").value,
    });
    $("#message").value = "";
    await refresh();
  } catch (error) {
    toast(error.message, true);
  } finally {
    state.busy = false;
    $("#send-message").disabled = false;
    $("#conversation-mode").textContent = "Ready to help, one thing at a time";
    $("#message").focus();
  }
}
async function createPlan(recipe, button) {
  return run(async () => {
    const task = await api("/api/tools", {
      name: "recipe_plan",
      arguments: {
        recipe,
        servings: Number($("#servings").value),
        less_spicy: $("#less-spicy").checked,
        language: $("#language").value,
      },
    });
    await refresh();
    $("#kitchen-results").replaceChildren(taskCard(task));
    toast("Cooking plan ready. Stock changes only after you mark it cooked.");
  }, button);
}
async function playSpeech(value, language, button) {
  await run(async () => {
    const result = await api("/api/speech/syntheses", {
      text: value,
      language,
    });
    const audio = new Audio(
      `data:${result.mime_type};base64,${result.audio_base64}`,
    );
    await audio.play();
  }, button);
}
document.addEventListener("click", async (event) => {
  const view = event.target.closest("[data-view]");
  if (view) {
    setView(view.dataset.view);
    return;
  }
  const prompt = event.target.closest("[data-prompt]");
  if (prompt) {
    await sendMessage(prompts[$("#language").value][prompt.dataset.prompt]);
    return;
  }
  const action = event.target.closest("[data-action]");
  if (!action) return;
  const task = state.data.tasks.find((task) => task.id === action.dataset.task);
  if (action.dataset.action === "review") {
    state.approval = task.id;
    const r = task.result;
    $("#approval-description").textContent =
      task.kind === "bill_preview"
        ? `${r.biller} · ${r.account} · ₹${(r.amount_paise / 100).toFixed(2)}`
        : `${r.origin} → ${r.destination} · ${r.date} · ₹${(r.amount_paise / 100).toFixed(2)}`;
    $("#approval-dialog").showModal();
  } else if (
    action.dataset.action === "cancel" ||
    action.dataset.action === "complete"
  ) {
    await run(async () => {
      const path =
        action.dataset.action === "cancel" ? "cancellation" : "completion";
      const result = await api(`/api/tasks/${task.id}/${path}`, {});
      await refresh();
      const kitchen = $("#kitchen-results");
      if (task.kind === "recipe_plan" && kitchen.childElementCount)
        kitchen.replaceChildren(taskCard(result));
      toast(
        action.dataset.action === "cancel"
          ? "Task cancelled."
          : "Meal recorded. Estimated stock deducted once.",
      );
    }, action);
  } else if (action.dataset.action === "plan") {
    setView("kitchen");
    $("#recipe").value = action.dataset.recipe;
    await createPlan(action.dataset.recipe, action);
  } else if (action.dataset.action === "stock") {
    const item = state.data.inventory.find(
      (item) => item.name === action.dataset.item,
    );
    $("#stock-name").value = item.name;
    $("#stock-quantity").value = item.quantity;
    $("#stock-unit").value = item.unit;
    $("#stock-dialog").showModal();
  }
});
$("#message-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const value = $("#message").value.trim();
  if (value) sendMessage(value);
});
$("#message").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    $("#message-form").requestSubmit();
  }
});
$("#new-chat").addEventListener("click", () =>
  run(async () => {
    state.session = crypto.randomUUID();
    localStorage.setItem("home-agent-session", state.session);
    await refresh();
    $("#message").focus();
  }),
);
$("#engine").addEventListener("change", renderConnections);
$("#language").value = localStorage.getItem("home-agent-language") || "en";
$("#language").addEventListener("change", () =>
  localStorage.setItem("home-agent-language", $("#language").value),
);
$("#dismiss-approval").addEventListener("click", () =>
  $("#approval-dialog").close(),
);
$("#confirm-approval").addEventListener("click", (event) =>
  run(async () => {
    await api(`/api/tasks/${state.approval}/approval`, {});
    $("#approval-dialog").close();
    await refresh();
    toast("Sandbox action completed. The result is saved in Activity.");
  }, event.currentTarget),
);
$("#receipt-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    const result = await api("/api/receipts", {
      text: $("#receipt-text").value,
      reference: $("#receipt-reference").value,
    });
    await refresh();
    toast(
      `Bill ${result.receipt_id} recorded. Repeating it will not duplicate stock.`,
    );
  }, event.submitter);
});
$("#stock-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    await api("/api/inventory/corrections", {
      name: $("#stock-name").value,
      quantity: $("#stock-quantity").value,
      unit: $("#stock-unit").value,
      reference: crypto.randomUUID(),
    });
    $("#stock-dialog").close();
    await refresh();
    toast("Stock corrected. The previous quantity remains in history.");
  }, event.submitter);
});
$("#recipe-form").addEventListener("submit", (event) => {
  event.preventDefault();
  createPlan($("#recipe").value, event.submitter);
});
$("#suggest-dishes").addEventListener("click", (event) =>
  run(async () => {
    const task = await api("/api/tools", {
      name: "dish_suggestions",
      arguments: { language: $("#language").value },
    });
    await refresh();
    $("#kitchen-results").replaceChildren(taskCard(task));
  }, event.currentTarget),
);
$("#booking-form").addEventListener("submit", (event) => {
  event.preventDefault();
  run(async () => {
    await api("/api/tools", {
      name: "booking_preview",
      arguments: {
        origin: $("#origin").value,
        destination: $("#destination").value,
        date: $("#travel-date").value,
        language: $("#language").value,
      },
    });
    await refresh();
    toast("Sandbox quote ready. Review and approve the task card.");
  }, event.submitter);
});
$("#audio-file").addEventListener("change", (event) =>
  run(async () => {
    const file = event.target.files[0];
    if (!file) return;
    if (!state.data.integrations.asr)
      throw new Error(
        "Indic transcription is not connected. Configure HOME_AGENT_ASR_URL first.",
      );
    if (file.size > 5000000)
      throw new Error("Choose an audio file under 5 MB.");
    const encoded = await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result.split(",")[1]);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
    const result = await api("/api/speech/transcriptions", {
      audio_base64: encoded,
      mime_type: file.type.split(";")[0],
      language: $("#language").value,
    });
    $("#message").value = result.text;
    $("#message").focus();
    toast("Transcribed. Review the text before sending.");
    event.target.value = "";
  }),
);
const tomorrow = new Date();
tomorrow.setDate(tomorrow.getDate() + 1);
$("#travel-date").value = [
  tomorrow.getFullYear(),
  String(tomorrow.getMonth() + 1).padStart(2, "0"),
  String(tomorrow.getDate()).padStart(2, "0"),
].join("-");
run(refresh);
