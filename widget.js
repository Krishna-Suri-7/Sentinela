// Sentinela Daily Budget Widget for Scriptable
// Add this to the Scriptable iOS app!

const API_URL = "https://sentinela-tdya.onrender.com/api/v1/summary/daily";

// Colors for aesthetic look
const COLORS = {
  bg: new Color("#1C1C1E"),
  textPrimary: new Color("#FFFFFF"),
  textSecondary: new Color("#8E8E93"),
  positive: new Color("#30D158"), // Green
  negative: new Color("#FF453A"), // Red
  accent: new Color("#0A84FF")    // Blue
};

async function fetchSummary() {
  try {
    let req = new Request(API_URL);
    // Timeout increased to 30s so the widget doesn't fail if the free cloud server is waking up from sleep
    req.timeoutInterval = 30;
    return await req.loadJSON();
  } catch (e) {
    return null;
  }
}

async function createWidget() {
  let widget = new ListWidget();
  widget.backgroundColor = COLORS.bg;
  
  let data = await fetchSummary();
  
  // Header
  let headerText = widget.addText("SENTINELA");
  headerText.font = Font.boldSystemFont(12);
  headerText.textColor = COLORS.accent;
  widget.addSpacer(8);
  
  if (!data) {
    let errText = widget.addText("Offline");
    errText.font = Font.systemFont(16);
    errText.textColor = COLORS.negative;
    return widget;
  }
  
  // Remaining Budget
  let amount = data.remaining;
  let isUnderBudget = data.status === "under_budget";
  
  let titleText = widget.addText("Today's Limit");
  titleText.font = Font.mediumSystemFont(14);
  titleText.textColor = COLORS.textSecondary;
  
  widget.addSpacer(2);
  
  let amountText = widget.addText(`€${amount.toFixed(2)}`);
  amountText.font = Font.boldSystemFont(32);
  amountText.textColor = isUnderBudget ? COLORS.positive : COLORS.negative;
  
  widget.addSpacer(8);
  
  // Daily Stats Footer
  let statsStack = widget.addStack();
  statsStack.layoutHorizontally();
  
  let spentLabel = statsStack.addText(`Spent: €${data.total_spent_today.toFixed(2)}`);
  spentLabel.font = Font.mediumSystemFont(12);
  spentLabel.textColor = COLORS.textSecondary;
  
  return widget;
}

let widget = await createWidget();
if (config.runsInWidget) {
  Script.setWidget(widget);
} else {
  widget.presentSmall();
}
Script.complete();
