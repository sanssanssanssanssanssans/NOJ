const key="noj-theme";
  function applyTheme(t){document.documentElement.classList.toggle("dark",t==="dark")}
  function detect(){const s=localStorage.getItem(key);if(s){return s}return window.matchMedia&&window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light"}
  let theme=detect();applyTheme(theme);
  document.getElementById("themeToggle").addEventListener("click",function(){theme=theme==="dark"?"light":"dark";localStorage.setItem(key,theme);applyTheme(theme)})
