// 팝업 보이기와 숨기기 로직
export function showPopup(popupId) {
    const popup = document.getElementById(popupId);
    popup.style.display = "flex";
    setTimeout(() => { popup.style.opacity = 1; }, 10);
  }
  
export  function hidePopup(popupId) {
    const popup = document.getElementById(popupId);
    popup.style.opacity = 0;
    setTimeout(() => { popup.style.display = "none"; }, 500);
  }