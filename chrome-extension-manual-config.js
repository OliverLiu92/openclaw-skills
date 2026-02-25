// 在 Chrome 控制台执行以下代码来手动设置 Gateway Token
// 步骤：
// 1. 打开 chrome://extensions
// 2. 找到 OpenClaw Browser Relay，点击"详情"
// 3. 点击"Service Worker"（背景页）
// 4. 在控制台粘贴以下代码：

chrome.storage.local.set({ 
  relayPort: 18792, 
  gatewayToken: "b3930ff4a8be31e815489cc0e36ad3943df095e17dfc41dd" 
}).then(() => {
  console.log("Gateway Token 已保存");
  chrome.storage.local.get(['relayPort', 'gatewayToken'], (data) => {
    console.log("当前配置:", data);
  });
});
